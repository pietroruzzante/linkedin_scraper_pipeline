import re


def pre_filter(offers, exclude_keywords):
    filtered = []
    discarded = []  
    print("Prefiltering...")
    for offer in offers:
        text = (offer["title"]+offer["description"]).lower()

        if not any(keyword.lower() in text for keyword in exclude_keywords):
            filtered.append(offer)

    return filtered

def split_offers(offers: list):
    # split the offers in chunks of 5
    for i in range(0, len(offers), 5):
        yield offers[i:i + 5]

def detect_language(offer: dict):
    spanish_words = ["para", "con", "los", "las", "del", "una", "por", "que", "buscamos", "requisitos"]
    text = offer["description"].lower()
    matches = sum(1 for w in spanish_words if re.search(r'\b' + w + r'\b', text))
    language =  "spanish" if matches >= 2 else "english"
    offer["language"] = language
    print(f"DEBUG: detected language: {language}")
    
    