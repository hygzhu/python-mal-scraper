import requests
import re
import json
from bs4 import BeautifulSoup


def basicData(url):
    data = {}

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    informationProperties = ["English", "Synonyms", "Japanese", "Episodes", "Status", "Aired", 
    "Broadcast",  "Source",  "Duration", "Rating", "Ranked", "Popularity", "Members", "Favorites"]

    for item in informationProperties:
        data[item] = soup.find('span', class_='dark_text', text=re.compile(item + ':')).__dict__['next_sibling'].strip()

    json_data = json.dumps(data)

    return json_data