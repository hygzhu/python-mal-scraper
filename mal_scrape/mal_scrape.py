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
        self.data = {}
        self.searchAnime()

    def searchAnime(self):
        """
        Queries for a myanimelist search result and sets first result to be scraped
        """
        try:
            page = requests.get("https://myanimelist.net/anime.php?q="+self.query)
            soup = BeautifulSoup(page.content, 'lxml')
            url = soup.find('a', class_='hoverinfo_trigger fw-b fl-l', href=True)['href']
            self.data['url'] = url
            page = requests.get(url)
            self.soup = BeautifulSoup(page.content, 'lxml')
            log('URL retrieved {}'.format(url))
        except Exception as e:
            log('Could not get get Anime')
        else:
            log('Found anime')

    def scrapeLeftMenu(self):
        """
        Scrapes the AlternativeTitles, Information and Statistics Section
        """
        basicTextInfo = ["English", "Synonyms", "Japanese", "Episodes", "Status", "Aired", 
        "Broadcast",  "Source",  "Duration", "Rating", "Ranked", "Popularity", "Members", "Favorites"]
        for item in basicTextInfo:
            try:
                self.data[item] = self.soup.find('span', class_='dark_text', text=re.compile(item + ':')).next_sibling.strip()
            except Exception as e:
                log('Could not get {}'.format(item))
            else:
                log('{} Found'.format(item))
        try:
            self.data['Premiered'] = self.soup.find('span', class_='dark_text', text=re.compile('Premiered:')).parent.find('a').next_element
        except Exception as e:
            log('Could not get Premiered')
        else:
            log('Premiered Found')

        multipleLinks = ["Producers", "Licensors", "Studios", "Genres"]
        for item in multipleLinks:
            try:
                self.data[item] = list(map( lambda x: x.next_element, self.soup.find('span', class_='dark_text', text=re.compile(item + ':')).parent.findAll('a')))
            except Exception as e:
                log('Could not get {}'.format(item))
            else:
                log('{} Found'.format(item))

        try:
            self.data["score"] = self.soup.find('span', itemprop='ratingValue').next_element
        except Exception as e:
            log('Could not get Score')
        else:
            log('Score Found')

        try:
            self.data["rating_count"] = self.soup.find('span', itemprop='ratingCount').next_element
        except Exception as e:
            log('Could not get Rating count')
        else:
            log('Rating count Found')

    def scrapeSynoposisBackground(self):
        """
        Scrapes info from the Synopsis, Background
        """
        try:
            self.data["synopsis"] = " ".join([str(x).replace('<br/>', '') for x in (list(self.soup.find('span', itemprop='description').children))]).replace('\"', '')
        except Exception as e:
            log('Could not get synopsis')
        else:
            log('synopsis count Found')
        try: 
            self.data["background"] = " ".join(list(map( lambda x: x if isinstance(x, str) else '', list(self.soup.find('h2', style='margin-top: 15px;').next_siblings)))).replace('  ', ' {} '.format(data["English"])).replace('\\', '').strip()
        except Exception as e:
            log('Could not get background')
        else:
            log('background count Found')

    def scrapeRelatedSection(self):
        """
        Scrapes the related section
        """
        relatedLinks =["Adaptation", "Side story", "Parent Story", "Full story", "Sequel", "Prequel", "Alternative version", "Alternative setting" "Prequel", "Other", "Summary", "Character", "Spin-off"]
        self.data['related'] = {}
        for item in relatedLinks:
            try:
                item_data = []
                item_list = list(map(lambda x: (x['href'], x.next_element) ,self.soup.find('td', class_='borderClass', text=re.compile(item+ ':')).parent.find_all('a')))
                for pair in item_list:
                    link_text= {
                        'link': pair[0],
                        'text': pair[1]
                    }
                    item_data.append(link_text)
                self.data['related'][item] = item_data
            except Exception as e:
                log('Could not get {}'.format(item))
            else:
                log('{} Found'.format(item))

    def scrapeCharactersVA(self):
        """
        Scrapes the Characters and Voice Actors section
        """
        try:
            left_char_info = [x for x in list(self.soup.find(class_="left-column fl-l divider").find_all('a')) if x.next_element != '\n']
            left_char_small = [ x.next_element for x in list(self.soup.find(class_="left-column fl-l divider").find_all('small')) ]
            self.data['characters_va'] = []
            for i, j in zip(left_char_info[0::2], left_char_info[1::2]):
                character_data = {
                    'name' : i.next_element,
                    'name_link' : i['href'],
                    'va' : j.next_element,
                    'va_link' : j['href'],
                    'status' : left_char_small[left_char_info.index(i)],
                    'language' : left_char_small[left_char_info.index(j)]
                    }
                self.data['characters_va'].append(character_data)
        except Exception as e:
            log('Could not get Characters section left side')
        else:
            log('Characters section left side Found')

        try:
            right_char_info = [x for x in list(self.soup.find(class_="left-right fl-r").find_all('a')) if x.next_element != '\n']
            right_char_small = [ x.next_element for x in list(self.soup.find(class_="left-right fl-r").find_all('small')) ]
            for i, j in zip(right_char_info[0::2], right_char_info[1::2]):
                character_data = {
                    'name' : j.next_element,
                    'name_link' : j['href'],
                    'va' : i.next_element,
                    'va_link' : i['href'],
                    'status' : right_char_small[right_char_info.index(i)],
                    'language' : right_char_small[right_char_info.index(j)]
                    }
                self.data['characters_va'].append(character_data)
        except Exception as e:
            log('Could not get Characters section left side')
        else:
            log('Characters section right side found')

    def scrapeOPED(self):
        #Scrapes opening/ending themes
        try:
            openings_data = [x.next_element for x in list(self.soup.find('div', class_='theme-songs js-theme-songs opnening').find_all('span' ,class_='theme-song'))]
            openings_data_list = []
            for i in openings_data:
                try:
                    songname = str(re.search(r'\".*\"', i)[0]).replace('\"', '')
                except Exception as e:
                    log('Could not get songname')
                else:
                    log('Got songname')
                try:
                    number = str(re.search(r'^#.*:', i)[0]).replace('#', '').replace(':', '')
                except Exception as e:
                    log('Could not get songname')
                else:
                    log('Got songname')
                try:
                    artists = str(re.search(r'\sby\s.*', i)[0]).replace('', '')
                except Exception as e:
                    log('Could not get songname')
                else:
                    log('Got songname')
                opening_data_item = {
                    'info': i,
                    'songname': songname,
                    'number': number,
                    'artists': artists
                }
                openings_data_list.append(opening_data_item)
                print(opening_data_item)
            self.data['openings'] = openings_data_list
        except Exception as e:
            log('Could not get Openings')
        else:
            log('Openings found')

        try:
            endings_data = [x.next_element for x in list(self.soup.find('div', class_='theme-songs js-theme-songs ending').find_all('span' ,class_='theme-song'))]
            endings_data_list = []
            for i in endings_data:
                try:
                    songname = str(re.search(r'\".*\"', i)[0]).replace('\"', '')
                except Exception as e:
                    log('Could not get songname')
                else:
                    log('Got songname')
                try:
                    number = str(re.search(r'^#.*:', i)[0]).replace('#', '').replace(':', '')
                except Exception as e:
                    log('Could not get songname')
                else:
                    log('Got songname')
                try:
                    artists = str(re.search(r'\sby\s.*', i)[0]).replace('', '')
                except Exception as e:
                    log('Could not get songname')
                else:
                    log('Got songname')
                ending_data_item = {
                    'info': i,
                    'songname': songname,
                    'number': number,
                    'artists': artists
                }
                endings_data_list.append(ending_data_item)
            self.data['endings'] = endings_data_list
        except Exception as e:
            log('Could not get Endings')
        else:
            log('Endings found')
    
    def getAnimeInfo(self):
        """
        Returns a JSON string containing information about the anime
        """
        start_time = time.time()
        self.scrapeLeftMenu()
        self.scrapeSynoposisBackground()
        self.scrapeRelatedSection()
        self.scrapeCharactersVA()
        self.scrapeOPED()

        json_data = json.dumps(self.data)
        log("Searching for the Anime info took --- %s seconds ---" % (time.time() - start_time))
        return json_data
