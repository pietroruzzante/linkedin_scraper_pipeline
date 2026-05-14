# set -a && source .env && set +a

import os
from scripts.linkedin_requests import request_offers
from scripts.parser import parse_offers
from scripts.utils import pre_filter, split_offers, detect_language
from scripts.llm_analysis import call_model, extract_keywords
from scripts.telegram_message import send_message, send_document, send_simple_message
from scripts.cv_parser import parse_cv
from scripts.customize_cv import customize_cv

import json

CV_PATH = os.environ["CV_PATH"]
TEMPLATE_PATH_EN = os.environ["TEMPLATE_PATH_EN"]
TEMPLATE_PATH_ES = os.environ["TEMPLATE_PATH_ES"]
OUTPUT_PATH = os.environ["OUTPUT_PATH"]

def handler(event, context):

    with open("config.json", "r") as f:
        config = json.load(f)
    # load config parameters
    search = config["searches"][0]
    name = search["name"]
    role = search["role"]
    location = search["location"]
    time_range_night = search["time_range_night"]
    time_range_day = search["time_range_day"]
    exclude_keywords = search["exclude_keywords"]
    priority_keywords = search["priority_keywords"]
    candidate_profile = search["candidate_profile"]

    greeting = config["telegram"]["greeting"]

    cv_config = config["cv"]
    competencies = cv_config["competencies"]
    libraries = cv_config["libraries"]
    languages = cv_config["languages"]
    tools = cv_config["tools"]

    # Request offers from Linkedin
    response = request_offers(role=role, location=location, time_range_night=time_range_night, time_range_day=time_range_day)

    # Parse offers, returns a json
    offers = parse_offers(response.text)
    print(f"Found {len(offers)} offers in total")

    # Pre-filter using exclude_keywords
    filtered_offers = pre_filter(offers, exclude_keywords)
    print(f"Found {len(filtered_offers)} offers after pre-filtering")

    # Parse cv from file
    print("Parsing CV...")
    cv_text = parse_cv(cv_path=CV_PATH)

    # Call model
    scored_offers = call_model(filtered_offers, priority_keywords, role, cv_text, candidate_profile)

    # Merge json 
    offers_by_id = {o["id"]: o for o in filtered_offers}
    scored_offers = [
        offers_by_id[o["id"]] | o
        for o in scored_offers
    ]
    offers_by_id = {o["id"]: o for o in scored_offers}

    # FIlter high score offers
    threshold = 8
    print("Filtering high score offers")
    high_score_offers_ids = [o["id"] for o in offers_by_id.values() if o["score"] >= threshold]
    low_score_offers_ids  = [o["id"] for o in offers_by_id.values() if o["score"] < threshold]

    print(f"DEBUG: high_score_offers_ids: {high_score_offers_ids}")
    print(f"DEBUG: low_score_offers_ids: {low_score_offers_ids}")

    if len(high_score_offers_ids) == 0:
        print("No high score offers found in this batch, sending simple message to telegram bot")
        send_simple_message(f"I couldn't find any offer with a score higher than {threshold}")

    # High score offers: customize cv, send message and pdf to telegram bot
    for id in high_score_offers_ids:
        offer = offers_by_id[id]
        print("------ new high score offer ----")
        print(f"DEBUG: High score JD company: {offer['company']}")
        detect_language(offer=offer)        

        # Extract relevant keyword 
        offer["keywords"] = extract_keywords(offer["description"])

        template_path = TEMPLATE_PATH_ES if offer["language"] == "spanish" else TEMPLATE_PATH_EN

        # Generate and save customized prompt
        doc_path = customize_cv(offer=offer, template_path=template_path, output_path=OUTPUT_PATH, name=name, candidate_profile=candidate_profile, competencies=competencies, libraries=libraries, languages=languages, tools=tools)

        # send message to telegram bot
        send_message(offer, greeting=greeting)

        #send pdf
        send_document(doc_path, caption = "")
    
    # Low score offers: send message to telegram bot
    send_simple_message(f"Here are some other offers that might be interesting for you, but with a lower score:")
    for id in low_score_offers_ids:
        offer = offers_by_id[id]
        send_message(offer)

if __name__ == "__main__":
    handler({}, None)
