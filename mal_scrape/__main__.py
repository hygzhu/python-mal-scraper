import argparse
import mal_scrape


def main():
    parser = argparse.ArgumentParser(description="Fetch MAL data")
    parser.add_argument('query', type=str, nargs=None, help='The Query string')
    parser.set_defaults(function=getInfo)

    args = parser.parse_args()
    try:
        args.function(args)
    except AttributeError:
        parser.print_help()

def getInfo(args):
    """
    Searches for the Anime Gets info from page
    """
    mal = mal_scrape.Mal_scrape(args.query)
    print(mal.getAnime()) 

if __name__ == "__main__":
    main()
