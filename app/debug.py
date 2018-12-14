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

html_test = '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Contrived Example</title>
        </head>
        <body>
            <p id="eggman">I am the egg man</p>
            <p id="walrus">I am the walrus</p>
        </body>
    </html>
'''

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
    except RequestException as e:
        log_error('Error during requests to {0}: {1}'.format(url, str(e)))


if __name__ == "__main__":
    no_html = simple_get_url('https://realpython.com/blog/nope-not-gonna-find-it')
    # print(no_html is None)
    
    bs_html = BeautifulSoup(html_test, "lxml")
    for index, value in enumerate(bs_html.select('body p'), 1):
        if value['id'] == "eggman":
            print(value.text)
