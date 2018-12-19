import json
import sys
from contextlib import closing

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

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
        <p>test</p>
    </html>
'''

def is_response(resp):
    # Returns True if the response seems to be HTML, False otherwise.
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('application/json') > -1)

def log_error(str):
    print(str)


def simple_get_url(url):
    try:
        with closing(get(url)) as resp:
            if is_response(resp):
                return resp.json()
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0}: {1}'.format(url, str(e)))


if __name__ == "__main__":
    my_json = simple_get_url('https://apps.juniper.net/cli-explorer/commands/list?sw=Junos%20OS')
    if (my_json is None):
        log_error('The request failed')
    else:
        with open('juniper-command.json', 'w', encoding='utf-8') as outfile:
            json.dump(my_json, outfile, indent=4, separators=(',', ': '), sort_keys=True)
            #add trailing newline for POSIX compatibility
            outfile.write('\n')
    
    
    # bs_html = BeautifulSoup(html_test, "lxml")
    # for index, value in enumerate(bs_html.select('body p'), 1):
    #     if value['id'] == "eggman":
    #         print(value.text)
