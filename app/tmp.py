import json
import os.path
import re
import sys
from contextlib import closing

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

from juniperbreadcrumbs import NewJuniperBreadcrumbs

# https://github.com/pkolt/design_patterns/blob/master/generating/builder.py
# https://www.giacomodebidda.com/factory-method-and-abstract-factory-in-python/

try:
    import ptvsd
    ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
    ptvsd.wait_for_attach()
    print('ptvsd is started')
except:
    print('ptvsd not working')


    def add_hierarchy(self, tmp_list):
        tmp = None
        for hierarchy_el in self.hierarchy:
            content = hierarchy_el.text + '/'
            tmp = [content+i for i in tmp_list]
        return tmp    
        
def main():
    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/tmp.html")
    with open(abs_path, 'r') as f:
        html = BeautifulSoup(f, 'lxml')
        
        hierarchy_statement = []
        syntax_statement = []
        if html.select_one("body > #app") is not None:
            new_breadcrumbs = NewJuniperBreadcrumbs(html)
            new_breadcrumbs.createHierarhyStatement().get_breadcrumbs()
        else:
            pass
        
          
        # breadcrumbs = Breadcrumbs(syntax_statement, hierarchy_statement)
            # breadcrumbs_list = breadcrumbs.get_breadcrumbs()
            # full_list = breadcrumbs.add_hierarchy(breadcrumbs_list)
            # print(full_list)

if __name__ == "__main__":
    main()
    
    # print('{} is depth {}'.format(value, depth))
