import requests
from datetime import datetime
import time

def request_offers(role: str, location: str, time_range_night: str, time_range_day: str) -> requests.Response:
    linkedin_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    time_range = time_range_night if datetime.now().hour == 9 else time_range_day

    params = {
    "keywords": role,
    "location": location,
    "f_TPR": time_range
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    return requests.get(linkedin_url, params=params, headers=headers)

def request_description(offer_link: str) -> str:
        time.sleep(1)
        return requests.get(offer_link).text