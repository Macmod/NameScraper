# TrailScraper

**TrailScraper** is a Selenium scraper for SecurityTrails public domain search tool. TrailScraper uses the [Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) to go through the result pages one by one and collect the full set of results from the supported lookups automatically.

## Supported Lookups

This tool can perform and collect the results for the following lookups in SecurityTrails:

* DNS
* Historical DNS
* Subdomains
* Reverse CNAME
* Reverse NS
* Reverse MX

# Prerequisites

- [Selenium](https://github.com/SeleniumHQ/Selenium)
- [Undetected Chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver)

Run the following to install the Python requirements:
```python
$ pip install -r requirements.txt
```

# Usage

In order to use TrailScraper you must have a SecurityTrails account, authenticate with it and save your `SecurityTrails` session cookie to a file named `session.txt`. Then run the tool with:

```bash
$ python trailscraper.py --lookup <LOOKUP_TYPE> --domain <DOMAIN> --output results.txt
```

If an output file is not provided with `--output`, the results are simply going to be printed to the screen. If you just want to get the subdomains for a domain, you can also omit the lookup type:

```bash
$ python trailscraper.py --domain <DOMAIN>
```

## Optional flags
- `--sessionfile` - Use a different file to load the session cookie (other than `session.txt`).
- `--domainsfile` - Look up all domains from a file in the same session instead of providing a single domain.
- `--timeout` - Default timeout to use in Selenium when looking for elements in the page.
- `--headless` - Run the webdriver in headless mode.

# Contributing

Contributions are welcome by [opening an issue](https://github.com/Macmod/TrailScraper/issues/new) or by [submitting a pull request](https://github.com/Macmod/TrailScraper/pulls). If you find any bugs please let me know - I don't have many test environments to validate every edge case.

# Todo

* Improve stability of simple DNS lookups (sometimes it works, sometimes it doesn't...)
* Support for explicit credentials and automatic reauthentication when the session expires
* Improve project structure and instructions
* Paginate historical DNS lookups

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
