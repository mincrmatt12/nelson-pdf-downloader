import queue
from multiprocessing.pool import ThreadPool
import functools
from tqdm import tqdm

def download(through_book, url):
    return through_book.send_request(url).content

def download_all(urls, through_book):
    with ThreadPool(4) as p:
        func = functools.partial(download, through_book)
        return list(tqdm(p.imap(func, urls), desc="Downloading PDFs", unit="file", total=len(urls)))
