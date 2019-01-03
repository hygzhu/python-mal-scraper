import argparse
import mal_scrape


def main():
    parser = argparse.ArgumentParser(description="Fetch MAL data")
    parser.add_argument('--query', type=str, help='The Query string')
    parser.add_argument('--getSeasonal', action='store_true', help='Get all seasonal anime')

    args = parser.parse_args()
    try:
        if(args.query):
            getInfo(args.query)
        elif(args.getSeasonal):
            getSeasonal()

    except AttributeError:
        parser.print_help()

def getInfo(query):
    """
    Searches for the Anime Gets info from page
    """
    mal = mal_scrape.Mal_scrape(query)
    mal.searchAnime()
    print(mal.getAnimeInfo()) 

def getSeasonal():
    mal = mal_scrape.Mal_scrape(None)
    mal.getSeasonal(2010,2019)

if __name__ == "__main__":
    main()
