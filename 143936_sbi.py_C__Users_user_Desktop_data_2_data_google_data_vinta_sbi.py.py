# coding: utf-8

import random
import re

# Python 3 compatibility
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from bs4 import BeautifulSoup
import requests


__version__ = '0.0.7'
__all__ = ['search_by', 'SBIResult', 'OhShitCAPTCHA']


class OhShitCAPTCHA(Exception):
    """
    Google: You Shall Not Pass!!!
    """


class SBIResult(object):

    def __init__(self):
        self.result_page = None
        self.all_sizes_page = None
        self.best_guess = None
        self.images = []

    def __bool__(self):
        return bool(self.images)

    __nonzero__ = __bool__

    def __len__(self):
        return len(self.images)

    def __repr__(self):
        return '<SBIResult [best_guess: %s]>' % (self.best_guess)

    def to_dict(self):
        return self.__dict__


# from: http://techblog.willshouse.com/2012/01/03/most-common-user-agents/
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9) AppleWebKit/537.71 (KHTML, like Gecko) Version/7.0 Safari/537.71',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:25.0) Gecko/20100101 Firefox/25.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0',
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
]

GOOGLE_BASE_URL = 'http://www.google.com/'
GOOGLE_SEARCH_BY_ENDPOINT = 'http://images.google.com/searchbyimage?hl=en&image_url='


def fire_request(url, referer):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4',
        'Cache-Control': 'no-cache',
        'Connection': 'close',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Referer': referer,
        'User-Agent': random.choice(USER_AGENTS),
    }

    r = requests.get(url, headers=headers)

    content = r.content

    return content


def cook_soup(text):
    soup = BeautifulSoup(text)

    captcha_input = soup.find_all('input', {'name': 'captcha'})
    if captcha_input:
        raise OhShitCAPTCHA

    return soup


def extract_best_guess(html):
    match = re.search(b'Best guess for this image.*?>(.*?)</a>', html, re.IGNORECASE | re.MULTILINE)

    if match:
        text = match.group(1)
        text = text.title()
    else:
        text = ''

    return text


def search_by(url=None, file=None):
    """
    TODO: support file
    """

    image_url = url
    # image_file = file

    """
    Search result page
    """

    result_url = GOOGLE_SEARCH_BY_ENDPOINT + image_url

    referer = 'http://www.google.com/imghp'
    result_html = fire_request(result_url, referer)

    result = SBIResult()
    result.result_page = result_url
    result.best_guess = extract_best_guess(result_html)

    soup = cook_soup(result_html)

    all_sizes_a_tag = soup.find('a', text='All sizes')

    # No other sizes of this image found
    if not all_sizes_a_tag:
        return result

    all_sizes_href = all_sizes_a_tag['href']
    all_sizes_url = urlparse.urljoin(GOOGLE_BASE_URL, all_sizes_href)

    result.all_sizes_page = all_sizes_url

    """
    All sizes page
    """

    all_sizes_html = fire_request(all_sizes_url, referer=all_sizes_url)

    soup = cook_soup(all_sizes_html)

    img_links =  soup.find_all('a', {'class': 'rg_l'})
    images = []
    for a in img_links:
        url = a['href']
        parse_result = urlparse.urlparse(url)

        querystring = parse_result.query
        querystring_dict = urlparse.parse_qs(querystring)

        image = {}
        image['url'] = querystring_dict['imgurl'][0]
        image['width'] = int(querystring_dict['w'][0])
        image['height'] = int(querystring_dict['h'][0])

        images.append(image)

    result.images = images

    return result
