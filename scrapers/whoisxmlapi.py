from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from re import search
from json import loads, dumps
import html2text
import tkinter as tk


class WhoisXMLAPIScraper():
    LOOKUP_MAP = {
        'subdomains': 'https://subdomains.whoisxmlapi.com/lookup',
        'reversens': 'https://reverse-ns.whoisxmlapi.com/lookup',
        'whois': 'https://whois.whoisxmlapi.com/lookup',
        'whoishistory': 'https://whois-history.whoisxmlapi.com/lookup',
        'reversewhois': 'https://reverse-whois.whoisxmlapi.com/lookup',
        'dnslookup': 'https://dns-lookup.whoisxmlapi.com/lookup',
        'dnshistory': 'https://dns-history.whoisxmlapi.com/lookup',
        'reversemx': 'https://reverse-mx.whoisxmlapi.com/lookup',
        'ipgeolocation': 'https://ip-geolocation.whoisxmlapi.com/lookup',
        'ipnetblocks': 'https://ip-netblocks.whoisxmlapi.com/lookup',
        'websitecontacts': 'https://website-contacts.whoisxmlapi.com/lookup',
        'websitecategorization': 'https://website-categorization.whoisxmlapi.com/lookup',
        'domainavailability': 'https://domain-availability.whoisxmlapi.com/lookup',
        'emailverification': 'https://emailverification.whoisxmlapi.com/lookup'
    }
    NEXT_BTN_XPATH = '//*[contains(@class, "common-colored-link") and contains(text(), "Next ")]'

    def __init__(self, driver, driver_wait,
                 session_cookie='',
                 output_file=None, html=False):
        self.driver = driver
        self.driver.get('https://www.whoisxmlapi.com/')
        self.driver.maximize_window()
        self.driver.add_cookie({
            'name': 'emailverification_session',
            'value': session_cookie,
            'domain': '.whoisxmlapi.com'
        })

        self.wait = driver_wait
        self.output_file = output_file

        self.text_maker = html2text.HTML2Text()
        self.text_maker.images_to_alt = True
        self.text_maker.ignore_tables = False
        self.text_maker.bypass_tables = False
        self.text_maker.ignore_links = True

        self.html = html

    def __selenium_scraper_generic(self, lookup_url, query):
        results = []
        self.driver.get(lookup_url)

        input_obj = self.wait.until(
            ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'input[name="search"]'
                )
            )
        )

        input_obj.clear()
        input_obj.send_keys(Keys.CONTROL + "a")
        input_obj.send_keys(query);

        submit_btn_obj = self.wait.until(
            ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'button[type="submit"]'
                )
            )
        )

        submit_btn_obj.click()

        next_page = True
        while next_page:
            try:
                copy_to_clipboard_btn = self.wait.until(
                    ec.presence_of_all_elements_located(
                        (
                            By.CSS_SELECTOR,
                            '.lookup-icons span'
                        )
                    )
                )
                copy_to_clipboard_btn[0].click()
            except Exception:
                continue

            result = loads(tk.Tk().clipboard_get())

            if self.output_file is not None:
                self.output_file.write(dumps(result) + '\n')
            else:
                print(dumps(result))

            results.append(result)

            try:
                link = self.wait.until(
                    ec.presence_of_element_located(
                        (
                            By.XPATH,
                            WhoisXMLAPIScraper.NEXT_BTN_XPATH
                        )
                    )
                )

                link.click()
            except Exception:
                print('[~] Could not find next page. Aborting...')
                next_page = False

        return results

    def lookup(self, query, lookup_type='subdomains'):
        result = self.__selenium_scraper_generic(
            WhoisXMLAPIScraper.LOOKUP_MAP[lookup_type], query
        )

        return result
