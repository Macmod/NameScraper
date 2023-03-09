from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import html2text


class ViewDNSScraper():
    LOOKUP_MAP = {
        'reverseip': 'https://viewdns.info/reverseip/?host=%s&t=1',
        'reversewhois': 'https://viewdns.info/reversewhois/?q=%s',
        'iphistory': 'https://viewdns.info/iphistory/?domain=%s',
        'dnsreport': 'https://viewdns.info/dnsreport/?domain=%s',
        'reversemx': 'https://viewdns.info/reversemx/?mx=%s',
        'reversens': 'https://viewdns.info/reversens/?ns=%s',
        'iplocation': 'https://viewdns.info/iplocation/?ip=%s',
        'chinesefirewall': 'https://viewdns.info/chinesefirewall/?domain=%s',
        'propagation': 'https://viewdns.info/propagation/?domain=%s',
        'ismysitedown': 'https://viewdns.info/ismysitedown/?domain=%s',
        'iranfirewall': 'https://viewdns.info/iranfirewall/?domain=%s',
        'whois': 'https://viewdns.info/whois/?domain=%s',
        'httpheaders': 'https://viewdns.info/httpheaders/?domain=%s',
        'dnsrecord': 'https://viewdns.info/dnsrecord/?domain=%s',
        'portscan': 'https://viewdns.info/portscan/?host=%s',
        'traceroute': 'https://viewdns.info/traceroute/?host=%s',
        'spamdblookup': 'https://viewdns.info/spamdblookup/?ip=%s',
        'reversedns': 'https://viewdns.info/reversedns/?ip=%s',
        'asnlookup': 'https://viewdns.info/asnlookup/?asn=%s',
        'ping': 'https://viewdns.info/ping/?domain=%s',
        'dnssec': 'https://viewdns.info/dnssec/?domain=%s',
        'abuselookup': 'https://viewdns.info/abuselookup/?domain=%s',
        'maclookup': 'https://viewdns.info/maclookup/?mac=%s',
        'freeemail': 'https://viewdns.info/freeemail/?domain=%s'
    }

    def __init__(self, driver, driver_wait, output_file=None, html=False):
        self.wait = driver_wait
        self.driver = driver

        self.driver.get('https://viewdns.info/')
        self.driver.maximize_window()

        self.output_file = output_file

        self.text_maker = html2text.HTML2Text()
        self.text_maker.images_to_alt = True
        self.text_maker.ignore_tables = False
        self.text_maker.bypass_tables = False
        self.text_maker.ignore_links = True

        self.html = html

    def __selenium_scraper_generic(self, lookup_url):
        self.driver.get(lookup_url)

        results_obj = self.wait.until(
            ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'tbody td>font[face="Courier"]'
                )
            )
        )

        results = None
        if results_obj:
            html = results_obj.get_attribute('innerHTML')
            if self.html:
                results = html
            else:
                results = self.text_maker.handle(html)

        if self.output_file is not None:
            self.output_file.write(results + '\n')
        else:
            print(results)

        return results

    def lookup(self, query, lookup_type='dnsrecord'):
        result = self.__selenium_scraper_generic(
            ViewDNSScraper.LOOKUP_MAP[lookup_type] % query
        )

        return result
