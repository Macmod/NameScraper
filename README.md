# NameScraper 

**NameScraper** is a Selenium scraper for public domain search tools. NameScraper uses the [Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) to perform queries in various platforms and collect the results.

## Disclaimer

This tool was developed for personal research purposes. I am not responsible for whatever actions are performed with this tool and I will not be maintaining it extensively or improving it to bypass captchas or other complex rate-limiting controls that these third-party tools may implement in the future.


## Supported Lookups

This tool can perform and collect the results for the following tools & lookups:

### SecurityTrails

In order to use this module you must have a SecurityTrails account, authenticate with it and save the contents of your `SecurityTrails` session cookie to a file named `session.txt`. Then run the tool with the appropriate `--lookup` flag:

* DNS (`dns`)
* Historical DNS (`historicaldns`)
* Subdomains (`subdomains` - **default lookup**)
* Reverse CNAME (`reversecname`)
* Reverse NS (`reversens`)
* Reverse MX (`reversemx`)

### ViewDNS

* ASN Lookup (`asnlookup`)
* Abuse Lookup (`abuselookup`)
* Chinese Firewall Test (`chinesefirewall`)
* DNS Record (`dnsrecord` - **default lookup**)
* DNS Report (`dnsreport`)
* DNSSEC (`dnssec`)
* Free Email (`freeemail`)
* HTTP Headers (`httpheaders`)
* IP History (`iphistory`)
* IP Location (`iplocation`)
* Iran Firewall Test (`iranfirewall`)
* Is my site down (`ismysitedown`)
* MAC Lookup (`maclookup`)
* Ping (`ping`)
* Portscan (`portscan`)
* Propagation (`propagation`)
* Reverse DNS (`reversedns`)
* Reverse IP (`reverseip`)
* Reverse MX (`reversemx`)
* Reverse NS (`reversens`)
* Reverse Whois (`reversewhois`)
* Spam DB lookup (`spamdblookup`)
* Traceroute (`traceroute`)
* Whois (`whois`)

Please note that ViewDNS's output format is not standard - it varies a lot depending on the type of the lookup, so the results are converted to text using the [html2text](https://github.com/Alir3z4/html2text) library. You'll probably have to parse the results somehow after using this tool.

### WhoisXMLAPI

In order to use this module you must have a WhoisXMLAPI account, authenticate with it and save the contents of your `emailverification_session` session cookie to a file named `session.txt`. Then run the tool with the appropriate `--lookup` flag:

* Subdomains (`subdomains` - **default lookup**)
* Reverse NS (`reversens`)
* Whois (`whois`)
* Whois History (`whoishistory`)
* Reverse Whois (`reversewhois`)
* DNS Lookup (`dnslookup`)
* DNS History (`dnshistory`)
* Reverse MX (`reversemx`)
* IP Geolocation (`ipgeolocation`)
* IP Netblocks (`ipnetblocks`)
* Website Contacts (`websitecontacts`)
* Website Categorization (`websitecategory`)
* Domain Availability (`domainavailability`)
* Email Verification (`emailverification`)

Note that currently this scraper has the limitation of using the `Copy to clipboard` feature of WhoisXMLAPI to copy the results as a JSON object, therefore you must *not use the clipboard for other purposes* while it's running.

# Prerequisites

- [Selenium](https://github.com/SeleniumHQ/Selenium)
- [Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

Run the following to install the Python requirements:
```python
$ pip install -r requirements.txt
```

# Usage

Run the tool with:

```bash
$ python namescraper.py --query <DOMAIN> --output results.txt <MODULE> --lookup <LOOKUP_TYPE>
```

If an output file is not provided with `--output`, the results are simply going to be printed to the screen. If you just want to use the default lookup for the provider, you can also omit the lookup type:

```bash
$ python namescraper.py --query <DOMAIN> <MODULE>
```

## Optional flags
- `--queriesfile` - Look up all lines from a file in the same session instead of providing a single query.
- `--timeout` - Default explicit timeout to use in Selenium when looking for elements in the page.
- `--headless` - Run the webdriver in headless mode.

# Contributing

Contributions are welcome by [opening an issue](https://github.com/Macmod/NameScraper/issues/new) or by [submitting a pull request](https://github.com/Macmod/NameScraper/pulls). If you find any bugs please let me know - I don't have many test environments to validate every edge case.

# Todo
* Perform more tests with all supported lookups and features to identify possible bugs
* Improve scraper logic to increase efficiency and avoid race conditions
* Improve project structure and instructions
* Improve error handling
* Support for explicit authentication credentials with automatic reauthentication when the session expires
* SecurityTrails - Improve stability of simple DNS lookups (sometimes it works, sometimes it doesn't...)
* SecurityTrails - Paginate historical DNS lookups
* WhoisXMLAPI - Use an alternate method of getting results in JSON without relying on the clipboard
* WhoisXMLAPI - Stop collection if the max limit for public queries is reached

# License
The MIT License (MIT)

Copyright (c) 2023 Artur Henrique Marzano Gonzaga

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
