import string
import random
import requests
import hashlib
import urllib3
import logging
from urllib.parse import urljoin
from concurrent.futures import as_completed, ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

MAX_WORKERS = 5
REQUEST_TIMEOUT = 5
# number of random URLs to test
TEST_COUNT = 10


def get_hash(body):
    return hashlib.md5(body.encode()).hexdigest()


def fetch_hash(base_url, path):
    url = urljoin(base_url, path)
    response = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False, allow_redirects=False)

    return get_hash(response.text)


def get_not_found_hashes(base_url):
    rand_paths = [''.join(random.choices(string.hexdigits, k=10)) for i in range(0, TEST_COUNT)]
    hashes = set()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_path = {executor.submit(fetch_hash, base_url, path): path for path in rand_paths}
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                hashes.add(future.result())
            except Exception as exc:
                logger.debug(f'{path} generated an exception: {exc}')

    return hashes
