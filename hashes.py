import string
import random
import requests
import hashlib
import urllib3
from urllib.parse import urljoin
from concurrent.futures import as_completed, ThreadPoolExecutor
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


MAX_WORKERS = 5
REQUEST_TIMEOUT = 5


def get_hash(body):
    return hashlib.md5(body.encode()).hexdigest()


def fetch_hash(base_url, path):
    url = urljoin(base_url, path)
    response = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False, allow_redirects=False)

    return get_hash(response.text)


def get_not_found_hashes(base_url):
    rand_paths = [''.join(random.choices(string.hexdigits, k=10)) for i in range(0, 10)]
    hashes = set()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Start the load operations and mark each future with its URL
        future_to_path = {executor.submit(fetch_hash, base_url, path): path for path in rand_paths}
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                hashes.add(future.result())
            except Exception as exc:
                print(f'{path} generated an exception: {exc}')

    return hashes
