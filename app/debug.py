import sys
from contextlib import closing

from requests import get
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

if ((len(sys.argv) > 1) and (sys.argv[1] == 'debug')):
    try:
        import ptvsd
        ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
        ptvsd.wait_for_attach()
        print('ptvsd is started')
    except:
        print('ptvsd not working')


def is_response(resp):
    # Returns True if the response seems to be HTML, False otherwise.
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('text/html') > -1)

def log_error(str):
    print(str)

def simple_get_url(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_response(resp):
                return resp
            else:
                return None
    except RequestException as identifier:
        log_error('Error during requests to {0}: {1}'.format(url, str(identifier)))



if __name__ == "__main__":
    no_html = simple_get_url('https://realpython.com/blog/nope-not-gonna-find-it')
    print(no_html is None)
