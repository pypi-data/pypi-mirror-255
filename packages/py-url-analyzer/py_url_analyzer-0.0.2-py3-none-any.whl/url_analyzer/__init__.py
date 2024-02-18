import requests
import validators
import time
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def analyze(url):
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url

    if not validators.url(url):
        raise ValueError("Invalid URL format")

    start_time = time.time()

    if start_time == 0:
        raise ValueError("Failed to initialize start_time")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch URL: {e}")

    end_time = time.time()
    load_time = end_time - start_time

    soup = BeautifulSoup(response.text, 'html.parser')

    http_requests_count = len(soup.find_all(['a', 'img', 'script', 'link'], href=True))        
    page_size = len(response.content)

    return {
        'load_time': f"{load_time:.2f}s",
        'http_requests_count': http_requests_count,
        'page_size': page_size
    }