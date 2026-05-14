from bs4 import BeautifulSoup
import json
from scripts.linkedin_requests import request_description

def parse_offers(html_string: str) -> json:

    soup = BeautifulSoup(html_string, "html.parser")

    li_offers = soup.find_all("li")
    offers = []
    print("Parsing offer")
    for i, offer in enumerate(li_offers):

        # Extract first information
        title_el = offer.find("h3", class_="base-search-card__title")
        company_el = offer.find("h4", class_="base-search-card__subtitle")
        location_el = offer.find("div", class_="base-search-card__metadata")
        link_el = offer.find("a")

        if not all([title_el, company_el, location_el, link_el]):
            continue

        company_a = company_el.find("a")
        location_span = location_el.find("span")

        if not all([company_a, location_span]):
            continue

        title = title_el.get_text(strip=True)
        company = company_a.get_text(strip=True)
        location = location_span.get_text(strip=True)
        link = link_el["href"]

        # Request description
        html_description = request_description(link)
        description = __parse_description(html_description)

        # offers dictionary list
        offers.append({
            "id": i,
            "title": title,
            "company": company,
            "location": location,
            "link": link,
            "description": description
        })

    return offers



def __parse_description(html_description):

    soup = BeautifulSoup(html_description, "html.parser")
    div = soup.find("div", class_="description__text")
    if div is None:
        return ""
    return div.get_text(strip=True)
