from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from json import dumps
import re


class SecurityTrailsScraper():
    LOOKUP_MAP = {
        'subdomains': 'https://securitytrails.com/list/apex_domain/%s',
        'reversens': 'https://securitytrails.com/list/ns/%s',
        'reversecname': 'https://securitytrails.com/list/cname/%s',
        'reversemx': 'https://securitytrails.com/list/mx/%s',
        'dnsrecord': 'https://securitytrails.com/domain/%s/dns',
        'historicaldns': 'https://securitytrails.com/domain/%s/history/%s'
    }
    NEXT_BTN_XPATH = './/*[contains(@class, "tooltip")]//li//a[text()="›"]'
    PAGINATION_REGEX = r'- ([\d,KBM+]+) of ([\d,KBM+]+) results'

    def __init__(self, driver, driver_wait,
                 session_cookie='', output_file=None):
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
                SecurityTrailsScraper.PAGINATION_REGEX,
                pagination_text
            ).groups()

            end_of_page = pagination_numbers[0]
            end_of_results = pagination_numbers[1]
        except Exception:
            end_of_page = 0
            end_of_results = 0

        return end_of_page, end_of_results

    def __selenium_scraper_domains(self, domain, lookup_type):
        domains = []

        self.driver.get(
            SecurityTrailsScraper.LOOKUP_MAP[lookup_type] % domain
        )

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
                        (By.XPATH, SecurityTrailsScraper.NEXT_BTN_XPATH)
                    )
                )
                next_page_btn.click()
            except Exception:
                print('[~] Could not find next page. Aborting...')
                break

        return domains

    def __selenium_scraper_dns(self, domain):
        results = {}

        self.driver.get(
            SecurityTrailsScraper.LOOKUP_MAP['dnsrecord'] % domain
        )

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
                SecurityTrailsScraper.LOOKUP_MAP['historical_dns'] % (domain, rtype)
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
        if lookup_type == 'dnsrecord':
            scraper = self.__selenium_scraper_dns
        elif lookup_type == 'historicaldns':
            scraper = self.__selenium_scraper_historical_dns
        else:
            def generic_domain_scraper(domain):
                return self.__selenium_scraper_domains(domain, lookup_type)

            scraper = generic_domain_scraper

        return scraper(domain)
