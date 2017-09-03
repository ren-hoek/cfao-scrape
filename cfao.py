"""Extract enforcement data from http://www.cfoa.org.uk/11823?."""
import csv
import re
import requests
from bs4 import BeautifulSoup


def create_soup(u):
    """Create beautiful soup object.

    Creates a html beautiful object from a url.
    Input:
        u: url to webpage
    Output:
        s: soup object representing page
    """
    req = requests.get(u)
    html = req.text
    s = BeautifulSoup(html, "html.parser")
    return s


def extract_postcode(s):
    """Extract validish UK Postcode.

    Uses regex from https://stackoverflow.com/questions/164979/uk-postcode-regex-comprehensive
    to extract a validish UK postcode from a string
    Input:
        s: string
    Output:
        p: postcode string
    """
    pc_regex = r'([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y]'
    pc_regex += r'[0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z]'
    pc_regex += r'))))\s?[0-9][A-Za-z]{2})'

    re_search = re.search(pc_regex, s)
    if re_search:
        p = re_search.group(0)
    else:
        p = ''
    return p


def clean_string(s):
    """Clean string.

    Clean string of everything but alpha-numeric, spaces,
    periods and colons.
    Replaces consecutive multiple spaces with single space.
    Input:
        s: raw text string
    Output:
        c: cleaned string
    """
    c = re.sub(r'\s+', ' ', re.sub(r'[^A-Za-z0-9 .:]', '', s))
    return c


def extract_search_count(p):
    """Extracts the search count.

    Extracts the total search hit count from a
    page of search results.
    Input:
        p: page of search hits
    Output:
        c: total number of search hits.
    """
    parsed_res = create_soup(p)
    c = parsed_res.find_all(
            'div',
            {'id': 'col2'}
    )[0].div.div.div.strong.text
    return c


def create_search_metadata(n, p, r):
    """Create search metadata.

    Creates a dictionary describing the search
    criteria and results.
    Input:
        n: name of search
        p: search parameters
        r: number of records
    Output:
        d: dictionary of metedata
    """
    d = dict()
    d['name'] = n
    d['params'] = p
    d['hits'] = r
    return d


def create_search_params(p):
    """Create search param string.
    Create search parameter string from a dictionary of pre-defined
    search paramters.
    Input:
        p: dictionary of parameters
    Output:
        s: search encoded string
    """
    param_temp = "premises_type_id={}&premise_id={}&frs_id={}&organisation_name={}&"
    param_temp += "responsible_person={}&address={}&address_postcode={}&status_id={}"

    s = param_temp.format(
        p['premises_type_id'],
        p['premises_id'],
        p['fire_service_id'],
        p['organisation_name'],
        p['responsible_person'],
        p['address'],
        p['postcode'],
        p['status_id']
    )
    return s


def create_cfoa_url(p, r, s):
    """Create cfoa search URL string.

    Create the search URL to extract notices from the www.cfoa.org.uk
    enforcement database.
    Input:
        p: search page number
        r: results per page
        s: encoded search parameters
    Output:
        u: string containing search url
    """
    base_url = "http://www.cfoa.org.uk/11823?pv=search&page={}&results_per_page={}&"
    u = base_url.format(p, r) + s
    return u


def calculate_num_scrape_pages(h, r):
    """Calculate number of pages to scrape.

    Calculate the number of pages required to scrape the
    full set of search documents
    Input:
        h: total number of search results
        r: number of results per page
    Output:
        p: number of scrape pages
    """
    p = (int(search_hits)/res_per_page) + 1
    return p


def create_header(e):
    """Create search entry header.

    Extract and create a dictionary from a search header.
    Input:
        e: div containing the serach entry
    Output:
        d: dictionary of search entry header
    """
    d = dict()
    link = e.find_all('a')[0].get('href')
    addr = e.find_all('a')[0].find_all(
        'span',
        {'class', 'enforce_result_link_text'}
    )[0].text
    enf = e.find_all('a')[0].find_all(
        'span',
        {'class', 'enforce_result_info'}
    )[0].text
    try:
        comp = clean_string(
            e.find_all('a')[0].find_all(
                'span',
                {'class', 'enforce_result_complied'}
            )[0].text
        )
    except IndexError:
        comp = clean_string(
            e.find_all('a')[0].find_all(
                'span',
                {'class', 'enforce_result_in_force'}
            )[0].text
        )

    d['addr'] = addr
    d['link'] = link
    d['enf'] = enf
    d['comp'] = comp
    return d


def create_detail(l):
    """Create detailed info for search result.

    Input:
        l: http link to search result page
    Output:
        d: dictionary of notice details
    """
    parsed_detail = create_soup(l)
    kv_pair = ""
    details = dict()
    for i in parsed_detail.find_all('tbody'):
        for j in i.find_all('tr'):
            for k in j.find_all('td'):
                cln = clean_string(k.text)
                if cln.find(":")<0:
                #if re.search(r'[A-Za-z]:', cln):
                    kv_pair += " " + cln
                else:
                    if len(kv_pair) > 0:
                        kv_process = kv_pair.split(":")
                        det_key = re.sub(
                                r'\s', '_', kv_process[0].strip()
                        ).lower()
                        details[det_key] = kv_process[1].strip()
                    kv_pair = cln
    return details


def create_search_results(p, r, s):
    """Create a dictionary from a page of search results.

    Create a dictionary from a page of search headers
    Input:
        p: search page number
        r: results per page
        s: encoded search parameters
    Output:
        d: list of search results
    """
    search_url = create_cfoa_url(p, r, s)

    parsed_res = create_soup(search_url)

    d = list()

    res_div = parsed_res.find_all(
            'div',
            {'class':
                ['enforce_result_container_complied',
                 'enforce_result_container_in_force']
            }
    )

    for i in res_div:
        entry = create_header(i)
        d.append(entry)
    return d


def create_notice_csv(d, f):
    """Create csv notice output.

    Create a csv file from the scraped notice data.
    Input:
        d: notice dictionary
        f: csv filename
    Output:
        True
    """
    header = list()
    for i in d[0].keys():
        if i != "search_details":
            try:
                for j in d[0][i].keys():
                    header.append(i+"."+j)
            except:
                header.append(i[1:])

    data = list()
    for e in d:
        row = list()
        for i in header:
            keys = i.split(".")
            if len(keys) == 2:
                row.append(e[keys[0]][keys[1]])
            elif len(keys) == 1:
                row.append(e["_" + keys[0]])
            else:
                continue

        data.append(row)

    with open(f, 'wb') as csv_file:
        csvwriter = csv.writer(csv_file, quoting=csv.QUOTE_NONNUMERIC)
        csvwriter.writerow(header)
        for row in data:
            csvwriter.writerow(row)
    return True


def scrape_result_pages(n, r, s):
    """Scrape search pages.

    Search the search result headers and return a list that
    includes the link to the detail page.
    Input:
        n: number of pages to scrape
        r: results per scrapped page
        s: search parameters
    Output:
        h: list of search headers
    """
    h = list()
    for page in xrange(n):
        for result in create_search_results(page + 1, r, s):
            h.append(result)
    return h


def scrape_detail_pages(h, s):
    """Scrape detailed notice pages.

    Scrape the notice detail for the results in the
    search header list.
    Input:
        h: list of search headers
        s: search metadata
    Output:
        n: list of search objects
    """
    n = list()
    for i, header in enumerate(h):
        notice = dict()
        notice['header'] = header
        print notice['header']['link']
        notice['detail'] = create_detail(notice['header']['link'])
        notice['detail']['postcode'] = (
            extract_postcode(notice['detail']['address'])
        )
        notice['search_details'] = s
        n.append(notice)
    return n

