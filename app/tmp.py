import json
import os.path
import re
import sys
from contextlib import closing


from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

from juniperbreadcrumbs import NewJuniperBreadcrumbs, OldJuniperBreadcrumbs
from constant import url_constant

# https://github.com/pkolt/design_patterns/blob/master/generating/builder.py
# https://www.giacomodebidda.com/factory-method-and-abstract-factory-in-python/
# https://www.juniper.net/documentation/en_US/junos/topics/reference/configuration-statement/aggregated-ether-options-interfaces-ex-series.html
# https://github.com/Patreon/patreon-python/blob/master/patreon/jsonapi/parser.py
# https://www.dev2qa.com/python-json-dump-to-or-load-from-file-example/
# https://github.com/rchristilaw/nhlapi/blob/develop/nhlapi/data_source/api.py
# https://github.com/jinchuuriki91/challenge-json-restructure/blob/master/script.py
# https://github.com/ctaylr13/shoppingCartJson
# https://compiletoi.net/fast-scraping-in-python-with-asyncio/

try:
    import ptvsd
    ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
    ptvsd.wait_for_attach()
    print('ptvsd is started')
except:
    print('ptvsd not working')

class Request(object):

    def getHtmlFromUrl(self, link):
        return self.__requestData(link)

    def getJsonFromUrl(self):
        resp =  self.__requestData(url_constant.BASE_JSON_FULL)
        if (resp is None):
            self.__log_error('The request failed')
        else:
            return resp.json()
    
    def __requestData(self, url):
        try:
            with closing(get(url)) as resp:
                if self.__is_response(resp):
                    return resp
                else:
                    return None
        except RequestException as e:
            self.__log_error('Error during requests to {0}: {1}'.format(url, str(e)))
   
    def __is_response(self, resp):
        # Returns True if the response seems to be HTML, False otherwise.
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and ((content_type.find('application/json') > -1) 
                or content_type.find('text/html') > -1))

    def __log_error(self, str):
        print(str)

class JuniperCommand(object):
    def __init__(self):
        dataSet = Request()


def main():
    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/old_tmp.html")
    with open(abs_path, 'r') as html_file:
        html = BeautifulSoup(html_file, 'lxml')

        # with open('/app/juniper-command.json', 'r') as file:
                
        # if html.select_one("body > #app") is not None:
        #     new_breadcrumbs = NewJuniperBreadcrumbs(html)
        #     new_breadcrumbs.createSyntaxStatement().get_breadcrumbs()
        #     new_breadcrumbs.createHierarhyStatement().get_breadcrumbs()
        #     tmp = new_breadcrumbs.merge()
        # else:
        #     new_breadcrumbs = OldJuniperBreadcrumbs(html)
        #     tmp = new_breadcrumbs.createHierarhyStatement().get_breadcrumbs()
        #     print('\n'.join(tmp))

if __name__ == "__main__":
    main()

    # print('{} is depth {}'.format(value, depth))
