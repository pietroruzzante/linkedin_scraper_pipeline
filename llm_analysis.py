import json
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from prompts import prompt_template_call_model, prompt_template_extract_keywords, cv_placeholder_prompt_template

os.environ["OPENAI_API_KEY"]

# Pydantic models
class ScoredOffer(BaseModel):
    id: int = Field(description="Unique identifier of the job offer")
    title: str = Field(description="Job title")
    company: str = Field(description="Name of the company offering the job")
    link: str = Field(description="URL to the job offer")
    score: int = Field(ge=1, le=10, description="Relevance score from 1 to 10, where 10 is the most relevant")
    comment: str = Field(description="A brief explanation of why the offer received that score, 1 sentence")
    summary: str = Field(description="A brief summary of the offer, 2-3 sentences")

class RankedOffers(BaseModel):
    offers: list[ScoredOffer]

class KeywordList(BaseModel):
    keywords: list[str]

class CVPlaceholders(BaseModel):
    ROLE: str
    CORE_COMPETENCIES: str
    LIBRARIES: str
    LANGUAGES: str
    TOOLS: str

#  LLM definition
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, model_kwargs={"seed": 42})
llm_strong = ChatOpenAI(model="gpt-4o", temperature=0)


# LangChain chains
_rank_chain = (
    ChatPromptTemplate.from_messages([
        ("system", prompt_template_call_model),
        ("human", "{offers}"),
    ])
    | llm.with_structured_output(RankedOffers, method="function_calling")
)


_keywords_chain = (
    ChatPromptTemplate.from_messages([
        ("system", prompt_template_extract_keywords),
        ("human", "{offer_description}"),
    ])
    | llm.with_structured_output(KeywordList, method="function_calling")
)

_placeholders_chain = (
    ChatPromptTemplate.from_messages([
        ("human", cv_placeholder_prompt_template),
    ])
    | llm_strong.with_structured_output(CVPlaceholders, method="function_calling")
)

def call_model(offers: list, priority_keywords: list, role: str, cv_text: str, candidate_profile: str) -> list:
    print("Requesting LLM analysis")
    result = _rank_chain.invoke({
        "role": role,
        "candidate_profile": candidate_profile,
        "cv": cv_text,
        "priority_keywords": json.dumps(priority_keywords),
        "offers": json.dumps(offers),
    })
    if isinstance(result, dict):
        result = RankedOffers(**result)
    return [o.model_dump() for o in result.offers]


def extract_keywords(offer_description: str) -> list[str]:
    print("Extract relevant keywords for every offer")
    result = _keywords_chain.invoke({"offer_description": offer_description})
    if isinstance(result, dict):
        result = KeywordList(**result)
    print(f"  → Extracted keywords: {result.keywords}")
    return result.keywords


def generate_placeholders(offer, candidate_profile, competencies, libraries, languages, tools) -> dict:
    print("Requesting LLM placeholder extraction...")
    result = _placeholders_chain.invoke({
        "profile": candidate_profile,
        "job_description": offer["description"],
        "keywords": json.dumps(offer["keywords"]),
        "competencies": competencies,
        "libraries": libraries,
        "languages": languages,
        "tools": tools,
    })
    if isinstance(result, dict):
        result = CVPlaceholders(**result)
    print(f"  → ROLE: {result.ROLE}")
    print(f"  → CORE_COMPETENCIES: {result.CORE_COMPETENCIES}")
    print(f"  → LIBRARIES: {result.LIBRARIES}")
    print(f"  → LANGUAGES: {result.LANGUAGES}")
    print(f"  → TOOLS: {result.TOOLS}")
    return result.model_dump()
