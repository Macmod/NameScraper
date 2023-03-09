from scrapers.viewdns import ViewDNSScraper
from scrapers.securitytrails import SecurityTrailsScraper
from scrapers.whoisxmlapi import WhoisXMLAPIScraper
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
import argparse
import sys

SUPPORTED_LOOKUPS = {
    'securitytrails': SecurityTrailsScraper.LOOKUP_MAP,
    'viewdns': ViewDNSScraper.LOOKUP_MAP,
    'whoisxmlapi':  WhoisXMLAPIScraper.LOOKUP_MAP
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='NameScraper is...')

    parser.add_argument('--timeout', default=10, type=int,
                        help='Default timeout to use in Selenium when looking for elements in the page.')
    parser.add_argument('--output', help='Output results to a file.')
    parser.add_argument('--queriesfile',
                        help='A file with lines to be looked up.')
    parser.add_argument('--query', help='The text to query.')
    parser.add_argument('--headless', action='store_true',
                        help='Run the webdriver in headless mode.')
    parser.add_argument('--sessionfile', default='session.txt',
                        help='File with the session cookie for the selected module.')

    subparsers = parser.add_subparsers(dest='module')

    parser_sectrails = subparsers.add_parser('securitytrails', help='SecurityTrails scraper.')
    parser_sectrails.add_argument('--lookup', default='subdomains',
                                  choices=SUPPORTED_LOOKUPS['securitytrails'],
                                  help='Type of the lookup to be performed.')

    parser_viewdns = subparsers.add_parser('viewdns', help='ViewDNS scraper.')
    parser_viewdns.add_argument('--lookup', default='subdomains',
                                choices=SUPPORTED_LOOKUPS['viewdns'],
                                help='Type of the lookup to be performed.')

    parser_whoisxmlapi = subparsers.add_parser('whoisxmlapi', help='WhoisXMLAPI scraper.')
    parser_whoisxmlapi.add_argument('--lookup', default='subdomains',
                                    choices=SUPPORTED_LOOKUPS['whoisxmlapi'],
                                    help='Type of the lookup to be performed.')

    args = parser.parse_args()

    specific_options = {}
    if args.module == 'securitytrails':
        module = 'SecurityTrails'
        scraper_class = SecurityTrailsScraper

        with open(args.sessionfile) as sessionfile:
            session_cookie = sessionfile.read().rstrip()

        specific_options['session_cookie'] = session_cookie
    elif args.module == 'viewdns':
        module = 'ViewDNS'
        scraper_class = ViewDNSScraper
    elif args.module == 'whoisxmlapi':
        module = 'WhoisXMLAPI'
        scraper_class = WhoisXMLAPIScraper

        with open(args.sessionfile) as sessionfile:
            session_cookie = sessionfile.read().rstrip()

        specific_options['session_cookie'] = session_cookie
    else:
        print('Unknown module selected. Please select one of the available modules (check --help).')
        sys.exit(1)

    print(f'[+] Selected module: "{module}"')
    lookup = args.lookup
    output_filepath = args.output

    # Initialize configs
    if output_filepath is not None:
        output_file = open(output_filepath, 'a+', encoding='utf-8')
        print(f'[+] Saving results to file "{output_filepath}"')
    else:
        output_file = None

    if not args.queriesfile and not args.query:
        print('[-] You must specify at least one of --queriesfile or --query to run the tool.')
        sys.exit(1)

    if args.queriesfile:
        with open(args.queriesfile) as queries_file:
            queries = list(map(lambda x: x.rstrip(), queries_file.readlines()))
    else:
        queries = [args.query]

    # Initialize Undetected Chrome with provided options
    options = uc.ChromeOptions()
    if args.headless:
        options.add_argument('--headless')

    driver = uc.Chrome(use_subprocess=True, options=options)
    driver_wait = WebDriverWait(driver, args.timeout)

    # Initialize scraper object from selected module's class
    scraper = scraper_class(
        driver, driver_wait,
        output_file=output_file,
        **specific_options
    )

    # Perform queries
    for query in queries:
        print(f'[+] Looking up "{query}" ({lookup})')
        scraper.lookup(query, lookup_type=lookup)

    if output_file is not None:
        output_file.close()
