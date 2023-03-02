from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import argparse
import re
import sys


class TrailScraper():
    def __init__(self, session_cookie, timeout=10, headless=False):
        options = uc.ChromeOptions() 
        if headless:
            options.add_argument('--headless')

        self.driver = uc.Chrome(use_subprocess=True, options=options)
        self.driver.get("https://securitytrails.com/")
        self.driver.maximize_window()
        self.driver.add_cookie({
            "name": "SecurityTrails",
            "value": session_cookie
        })

        self.driver.implicitly_wait(timeout)
        self.wait = WebDriverWait(self.driver, timeout)

    def __extract_pagination(self):
        try:
            pagination = self.wait.until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, 'pagination-details')
                )
            )
            pagination_text = pagination.text.replace('\n', ' ').replace('\r', ' ')
            pagination_numbers = re.search(
                r'- ([\d,BM+]+) of ([\d,BM+]+) results',
                pagination_text
            ).groups()

            end_of_page = pagination_numbers[0]
            end_of_results = pagination_numbers[1]
        except Exception:
            end_of_page = 0
            end_of_results = 0

        return end_of_page, end_of_results

    def trail_scraper(self, lookup_url, output_file):
        domains = []

        self.driver.get(lookup_url)

        end_of_page, end_of_results = (100, -1)
        while end_of_page != end_of_results:
            sample = self.driver.find_elements(By.CSS_SELECTOR, "tbody>tr a")
            try:
                page_domains = [el.text for el in sample]
            except Exception:
                pass

            if output_file is not None:
                output_file.write('\n'.join(page_domains) + '\n')
            else:
                print('\n'.join(page_domains))

            domains += page_domains

            end_of_page, end_of_results = self.__extract_pagination()

            try:
                next_page_btn = self.wait.until(
                    ec.presence_of_element_located(
                        (By.XPATH, './/*[contains(@class, "tooltip")]//li//a[text()="›"]')
                    )
                )
                next_page_btn.click()
            except Exception:
                print('[~] Could not find next page. Aborting...')
                break

        n_domains = len(domains)
        print(f'[+] {n_domains} domains found.')

        return domains

    def subdomain_sample(self, domain, output_file):
        lookup_url = f"https://securitytrails.com/list/apex_domain/{domain}"
        results = self.trail_scraper(lookup_url, output_file)
        return results

    def reverse_ns_sample(self, domain, output_file):
        lookup_url = f"https://securitytrails.com/list/ns/{domain}"
        results = self.trail_scraper(lookup_url, output_file)
        return results

    def reverse_cname_sample(self, domain, output_file):
        lookup_url = f"https://securitytrails.com/list/cname/{domain}"
        results = self.trail_scraper(lookup_url, output_file)
        return results

    def reverse_mx_sample(self, domain, output_file):
        lookup_url = f"https://securitytrails.com/list/mx/{domain}"
        results = self.trail_scraper(lookup_url, output_file)
        return results

if __name__ == '__main__':
    SUPPORTED_LOOKUPS = [
        'subdomains', 'reverse_ns', 'reverse_cname', 'reverse_mx'
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
    parser.add_argument('--domainsfile', 
                        help='A file with domains to be looked up.')
    parser.add_argument('--domain', help='The domain to look up.')
    parser.add_argument('--headless', action='store_true', help='Run the webdriver in headless mode.')
    args = parser.parse_args()

    domains = []
    lookup = args.lookup
    output_filepath = args.output

    with open(args.sessionfile) as sessionfile:
        session_cookie = sessionfile.read().rstrip()

    ts = TrailScraper(session_cookie,
                      timeout=args.timeout,
                      headless=args.headless)

    lookup_methods = {
        'subdomains': ts.subdomain_sample,
        'reverse_ns': ts.reverse_ns_sample,
        'reverse_cname': ts.reverse_cname_sample,
        'reverse_mx': ts.reverse_mx_sample
    }

    if lookup not in lookup_methods:
        print(f'[+] Invalid lookup "{lookup}".')
        sys.exit(1)

    lookup_fn = lookup_methods[lookup]

    if not args.domainsfile and not args.domain:
        print('[-] You must specify at least one of --domainsfile or --domain to run the tool.')
        sys.exit(1)

    if args.domainsfile:
        with open(args.domainsfile) as domains_file:
            domains = list(map(lambda x: x.rstrip(), domains_file.readlines()))
    else:
        domains = [args.domain]

    if output_filepath is not None:
        output_file = open(output_filepath, 'a+')
        print(f'[+] Saving results to file "{output_filepath}"')
    else:
        output_file = None

    for domain in domains:
        print(f'[+] Looking up domain "{domain}"')
        lookup_fn(domain, output_file)

    if output_file is not None:
        output_file.close()
