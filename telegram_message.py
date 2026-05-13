import requests
import os

token = os.environ["TELEGRAM_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]
url = f"https://api.telegram.org/bot{token}/sendMessage"

def send_simple_message(text: str):
    print("Sending message...")
    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": text
    })

def send_message(offer: dict, greeting: str = "Hello!"):

    caption = f"""
        {greeting}
        I found this offer for you
        {offer["title"]}, {offer["company"]} 
        {offer["location"]}
        --------
        {offer["summary"]}
        --------
        score: {offer["score"]}
        comment: {offer["comment"]}
        --------
        {offer["link"]}
    """

    print("Sending message...")
    response = requests.post(url, json={
        "chat_id": chat_id,
        "text": caption
    })

    #print(response.json())

def send_document(file_path: str, caption: str = ""):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    
    with open(file_path, "rb") as f:
        response = requests.post(url, data={
            "chat_id": chat_id,
            "caption": caption
        }, files={
            "document": f
        })
    
    print(response.json())