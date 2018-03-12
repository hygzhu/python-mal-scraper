import argparse
import mal_scrape


def main():
    parser = argparse.ArgumentParser(description="Fetch MAL data")

    subparsers = parser.add_subparsers(help='sub-command help')

    info_parser = subparsers.add_parser('info', help='Get Info')
    info_parser.add_argument('url', type=str, help='URL of MAL page')
    info_parser.set_defaults(function=getInfo)

    args = parser.parse_args()
    try:
        args.function(args)
    except AttributeError:
        parser.print_help()

def getInfo(args):
    """
    Gets info from page
    """
    print(mal_scrape.basicData(args.url)) 

if __name__ == "__main__":
    main()
