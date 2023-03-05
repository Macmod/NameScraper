from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from json import dumps
import argparse
import re
import sys


class TrailScraper():
    DOMAIN_LOOKUP_MAP = {
        'subdomains': 'https://securitytrails.com/list/apex_domain/%s',
        'reverse_ns': 'https://securitytrails.com/list/ns/%s',
        'reverse_cname': 'https://securitytrails.com/list/cname/%s',
        'reverse_mx': 'https://securitytrails.com/list/mx/%s'
    }
    NEXT_BTN_XPATH = './/*[contains(@class, "tooltip")]//li//a[text()="›"]'
    PAGINATION_REGEX = r'- ([\d,BM+]+) of ([\d,BM+]+) results'

    def __init__(self, driver, driver_wait,
                 session_cookie, output_file=None):
        self.driver = driver
        self.wait = driver_wait

        self.driver.get('https://securitytrails.com/')
        self.driver.maximize_window()
        self.driver.add_cookie({
            'name': 'SecurityTrails',
            'value': session_cookie
        })

        self.output_file = output_file

    def __extract_pagination(self):
        try:
            pagination_obj = self.wait.until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, 'pagination-details')
                )
            )
            pagination_text = pagination_obj.text.replace('\n', ' ')
            pagination_text = pagination_text.replace('\r', ' ')
            pagination_numbers = re.search(
                TrailScraper.PAGINATION_REGEX,
                pagination_text
            ).groups()

            end_of_page = pagination_numbers[0]
            end_of_results = pagination_numbers[1]
        except Exception:
            end_of_page = 0
            end_of_results = 0

        return end_of_page, end_of_results

    def __selenium_scraper_domains(self, lookup_url):
        domains = []

        self.driver.get(lookup_url)

        end_of_page, end_of_results = (100, -1)
        while end_of_page != end_of_results:
            sample = self.driver.find_elements(By.CSS_SELECTOR, "tbody>tr a")
            try:
                page_domains = [el.text for el in sample]
            except Exception:
                pass

            if self.output_file is not None:
                self.output_file.write('\n'.join(page_domains) + '\n')
            else:
                print('\n'.join(page_domains))

            domains += page_domains

            end_of_page, end_of_results = self.__extract_pagination()

            try:
                next_page_btn = self.wait.until(
                    ec.presence_of_element_located(
                        (By.XPATH, TrailScraper.NEXT_BTN_XPATH)
                    )
                )
                next_page_btn.click()
            except Exception:
                print('[~] Could not find next page. Aborting...')
                break

        return domains

    def __selenium_scraper_dns(self, domain):
        results = {}

        self.driver.get(f'https://securitytrails.com/domain/{domain}/dns')

        grid_divs = self.wait.until(
            ec.presence_of_all_elements_located(
                (
                    By.CSS_SELECTOR, "#app-content>.grid>div"
                )
            )
        )

        for grid_div in grid_divs:
            inner_divs = grid_div.find_elements(By.CSS_SELECTOR, "div")
            info_type = inner_divs[0].text

            if info_type.endswith('records'):
                records_els = inner_divs[1].find_elements(
                    By.CSS_SELECTOR,
                    'a.link'
                )
                records = [r.text for r in records_els]

                normalized_info_type = info_type.replace(' records', '')

                results[normalized_info_type] = records
            elif info_type == 'TXT':
                records_els = inner_divs[1].find_elements(
                    By.CSS_SELECTOR, 'span'
                )
                records = [r.text for r in records_els]
                results['TXT'] = records
            else:
                continue

        if self.output_file is not None:
            self.output_file.write(dumps(results) + '\n')
        else:
            print(dumps(results))

        return results

    def __selenium_scraper_historical_dns(self, domain):
        results = []
        record_types = ['a', 'aaaa', 'mx', 'ns', 'soa', 'txt']

        for rtype in record_types:
            subresults = []

            self.driver.get(
                f'https://securitytrails.com/domain/{domain}/history/{rtype}'
            )

            table = self.wait.until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, 'ui-table')
                )
            )
            keys_els = table.find_elements(By.CSS_SELECTOR, 'thead th')
            keys = [k.text for k in keys_els]

            rows_els = table.find_elements(By.CSS_SELECTOR, 'tbody tr')
            for row_el in rows_els:
                cols_els = row_el.find_elements(By.CSS_SELECTOR, 'td')

                cols = {}
                for x in range(len(keys)):
                    col_value = cols_els[x].text
                    if '\n' in col_value:
                        col_value = col_value.split('\n')
                    cols[keys[x]] = col_value

                subresults.append(cols)

            result_obj = {'type': rtype, 'results': subresults}
            if self.output_file is not None:
                self.output_file.write(dumps(result_obj) + '\n')
            else:
                print(dumps(result_obj))
            results.append(result_obj)

        return results

    def lookup(self, domain, lookup_type='subdomains'):
        if lookup_type == 'dns':
            results = self.__selenium_scraper_dns(domain)
        elif lookup_type == 'historical_dns':
            results = self.__selenium_scraper_historical_dns(domain)
        else:
            lookup_url = TrailScraper.DOMAIN_LOOKUP_MAP[lookup_type] % domain
            results = self.__selenium_scraper_domains(lookup_url)

        return results


if __name__ == '__main__':
    SUPPORTED_LOOKUPS = [
        'subdomains',
        'reverse_ns',
        'reverse_cname',
        'reverse_mx',
        'dns',
        'historical_dns'
    ]

    parser = argparse.ArgumentParser(
        description='TrailScraper is a Selenium scraper for SecurityTrails public domain search supporting lookups for subdomains & reverse NS/CNAME/MX.'
    )
    parser.add_argument('--timeout', default=10, type=int,
                        help='Default timeout to use in Selenium when looking for elements in the page.')
    parser.add_argument('--lookup', default='subdomains',
                        choices=SUPPORTED_LOOKUPS,
                        help='Type of the lookup to be performed.')
    parser.add_argument('--output', help='Output results to a file.')
    parser.add_argument('--sessionfile', default='session.txt',
                        help='A file with your SecurityTrails cookie.')
    parser.add_argument('--queriesfile',
                        help='A file with queries to be looked up.')
    parser.add_argument('--query', help='The query to look up.')
    parser.add_argument('--headless', action='store_true',
                        help='Run the webdriver in headless mode.')
    args = parser.parse_args()

    domains = []
    lookup = args.lookup
    output_filepath = args.output

    with open(args.sessionfile) as sessionfile:
        session_cookie = sessionfile.read().rstrip()

    if output_filepath is not None:
        output_file = open(output_filepath, 'a+')
        print(f'[+] Saving results to file "{output_filepath}"')
    else:
        output_file = None

    options = uc.ChromeOptions()
    if args.headless:
        options.add_argument('--headless')

    driver = uc.Chrome(use_subprocess=True, options=options)
    driver.implicitly_wait(args.timeout)
    driver_wait = WebDriverWait(driver, args.timeout)

    ts = TrailScraper(driver, driver_wait,
                      session_cookie,
                      output_file=output_file)

    if not args.queriesfile and not args.query:
        print('[-] You must specify at least one of --queriesfile or --query to run the tool.')
        sys.exit(1)

    if args.queriesfile:
        with open(args.queriesfile) as queries_file:
            queries = list(map(lambda x: x.rstrip(), queries_file.readlines()))
    else:
        queries = [args.query]

    for query in queries:
        print(f'[+] Looking up "{query}" ({lookup})')
        results = ts.lookup(query, lookup_type=lookup)
        n_results = len(results)
        print(f'[+] {n_results} results found.')

    if output_file is not None:
        output_file.close()
