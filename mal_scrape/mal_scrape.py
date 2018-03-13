import requests
import re
import json
from bs4 import BeautifulSoup

#speed test
import time

DEBUG = False

def log(s):
    if DEBUG:
        print(s)


class Mal_scrape:

    def __init__(self, query):
        self.query = query

    def getAnime(self):
        """
        Returns a JSON string containing information about the anime
        """
        data = {}
        start_time = time.time()

        #Queries for a myanimelist search result
        page = requests.get("https://myanimelist.net/anime.php?q="+self.query)
        soup = BeautifulSoup(page.content, 'lxml')
        url = soup.find('a', class_='hoverinfo_trigger fw-b fl-l', href=True)['href']
        data['url'] = url

        #Scrapes the first page for information
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'lxml')
        log('URL retrieved {}'.format(url))


        #Scrapes the AlternativeTitles, Information and Statistics Section
        basicTextInfo = ["English", "Synonyms", "Japanese", "Episodes", "Status", "Aired", 
        "Broadcast",  "Source",  "Duration", "Rating", "Ranked", "Popularity", "Members", "Favorites"]
        for item in basicTextInfo:
            try:
                data[item] = soup.find('span', class_='dark_text', text=re.compile(item + ':')).next_sibling.strip()
            except AttributeError:
                log('Could not get {}'.format(item))
            else:
                log('{} Found'.format(item))

        try:
            data['Premiered'] = soup.find('span', class_='dark_text', text=re.compile('Premiered:')).parent.find('a').next_element
        except AttributeError:
            log('Could not get Premiered')
        else:
            log('Premiered Found')

        multipleLinks = ["Producers", "Licensors", "Studios", "Genres"]
        for item in multipleLinks:
            try:
                data[item] = list(map( lambda x: x.next_element, soup.find('span', class_='dark_text', text=re.compile(item + ':')).parent.findAll('a')))
            except AttributeError:
                log('Could not get {}'.format(item))
            else:
                log('{} Found'.format(item))

        try:
            data["score"] = soup.find('span', itemprop='ratingValue').next_element
        except AttributeError:
            log('Could not get Score')
        else:
            log('Score Found')

        try:
            data["rating_count"] = soup.find('span', itemprop='ratingCount').next_element
        except AttributeError:
            log('Could not get Rating count')
        else:
            log('Rating count Found')

        #Scrapes info from the Synopsis, Background
        try:
            data["synopsis"] = " ".join([str(x).replace('<br/>', '') for x in (list(soup.find('span', itemprop='description').children))]).replace('\"', '')
        except AttributeError:
            log('Could not get synopsis')
        else:
            log('synopsis count Found')
        try: 
            data["background"] = " ".join(list(map( lambda x: x if isinstance(x, str) else '', list(soup.find('h2', style='margin-top: 15px;').next_siblings)))).replace('  ', ' {} '.format(data["English"])).replace('\\', '').strip()
        except AttributeError:
            log('Could not get background')
        else:
            log('background count Found')

        #Scrapes the related section
        relatedLinks =["Adaptation", "Side story", "Parent Story", "Full story", "Sequel", "Prequel", "Alternative version", "Alternative setting" "Prequel", "Other", "Summary", "Character", "Spin-off"]
        for item in relatedLinks:
            try:
                data[item] = list(map(lambda x: [x['href'], x.next_element] ,soup.find('td', class_='borderClass', text=re.compile(item+ ':')).parent.find_all('a')))
            except AttributeError:
                log('Could not get {}'.format(item))
            else:
                log('{} Found'.format(item))

        json_data = json.dumps(data)
        log("Searching for the Anime info took --- %s seconds ---" % (time.time() - start_time))
        return json_data
