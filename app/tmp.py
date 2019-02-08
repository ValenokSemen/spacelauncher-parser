import json
import os.path
import re
import sys
from contextlib import closing

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

from juniperbreadcrumbs import NewJuniperBreadcrumbs, OldJuniperBreadcrumbs

# https://github.com/pkolt/design_patterns/blob/master/generating/builder.py
# https://www.giacomodebidda.com/factory-method-and-abstract-factory-in-python/
# https://www.juniper.net/documentation/en_US/junos/topics/reference/configuration-statement/aggregated-ether-options-interfaces-ex-series.html
# https://github.com/Patreon/patreon-python/blob/master/patreon/jsonapi/parser.py

try:
    import ptvsd
    ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
    ptvsd.wait_for_attach()
    print('ptvsd is started')
except:
    print('ptvsd not working')

      
def main():
    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/old_tmp.html")
    with open(abs_path, 'r') as f:
        html = BeautifulSoup(f, 'lxml')        
        if html.select_one("body > #app") is not None:
            new_breadcrumbs = NewJuniperBreadcrumbs(html)
            new_breadcrumbs.createSyntaxStatement().get_breadcrumbs()
            new_breadcrumbs.createHierarhyStatement().get_breadcrumbs()
            tmp = new_breadcrumbs.merge()
        else:
            new_breadcrumbs = OldJuniperBreadcrumbs(html)
            tmp = new_breadcrumbs.createHierarhyStatement().get_breadcrumbs()
            print('\n'.join(tmp))

if __name__ == "__main__":
    main()
    
    # print('{} is depth {}'.format(value, depth))
