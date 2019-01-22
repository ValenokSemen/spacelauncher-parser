import json
import sys
from contextlib import closing
import os.path

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

try:
    import ptvsd
    ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
    ptvsd.wait_for_attach()
    print('ptvsd is started')
except:
    print('ptvsd not working')
        
if __name__ == "__main__":
    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/tmp.html")
    with open(abs_path, 'r') as f:
        html = BeautifulSoup(f, 'lxml')
        get_syntax = html.select_one("sw-code")
        
        for index, value in enumerate(get_syntax.select(".statement"), 1):
            print(value.text)

    
