import json
import os.path
import re
import sys
from contextlib import closing

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

from JuniperBreadcrumbs import NewJuniperBreadcrumbs

# https://github.com/pkolt/design_patterns/blob/master/generating/builder.py

try:
    import ptvsd
    ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
    ptvsd.wait_for_attach()
    print('ptvsd is started')
except:
    print('ptvsd not working')

class Rematcher(object):

    def __init__(self, matchstring):
         self.matchstring = matchstring.replace(';', '')
         self.is_header = None

    def get_header(self):
        return self.is_header    
    
    def is_match(self, regexp):
        self.rematch = re.search(regexp, self.matchstring)
        return bool(self.rematch)
    
    def group(self, regexp):
        self.rematch = re.match(regexp, self.matchstring) 
        if self.rematch:
            self.is_header = True

    def split(self):
        split_data =  re.split(r'\s+|\[|\]', self.matchstring)
        self.mylist = [i for i in split_data if i]

class Breadcrumbs(object):

    __crumbs = []
    __elem_crumbs = ['']*20

    def __init__(self, syntax_list, hierarchy_list):
        self.syntax = syntax_list
        self.hierarchy = hierarchy_list
    
    @property
    def syntax(self):
        # statement getter
        return self.__syntax
    
    @syntax.setter
    def syntax(self, syntax):
        # statement setter
        self.__syntax = syntax
    
    @property
    def hierarchy(self):
        # statement getter
        return self.__hierarchy
    
    @hierarchy.setter
    def hierarchy(self, hierarchy):
        # statement setter
        self.__hierarchy = hierarchy

    @property
    def depth(self):
        # statement getter
        return self.__depth
    
    @depth.setter
    def depth(self, depth):
        # statement setter
        self.__depth = depth

    def set_statement_depth(self, statement_element):
        self.depth = 0
        if ("ind-statement" in statement_element.get('class')):
            self.depth += 1 
        upper_parent = statement_element.parent
        while (upper_parent.name != 'sw-code'):
            self.depth += 1      
            upper_parent = upper_parent.parent

    def clean_statement(self, statement_element):
        pattern = re.compile(r'(\n\s+|\n)')
        return pattern.sub(' ', statement_element.text).replace(' {', '')

    def get_breadcrumbs(self):
        for statement_el in self.syntax:
            self.set_statement_depth(statement_el)
            clean_statement_el = self.clean_statement(statement_el)
            m = Rematcher(clean_statement_el)
            if m.is_match(r'(\(|\||\[)'):
                m.group(r'^(\w[0-9a-zA-Z-_]+)')
                m.split()
                if m.get_header:
                    for i, value in enumerate(m.mylist, 1):
                        if (i == 2):
                            self.depth += 1
                        self.set_breadcrumbs(value)
                else:
                    for i, value in enumerate(m.mylist, 1):
                        self.set_breadcrumbs(value)

                continue
            if re.match(r'^}', clean_statement_el) is None:
                self.set_breadcrumbs(clean_statement_el)
        return self.__crumbs 

    def add_hierarchy(self, tmp_list):
        tmp = None
        for hierarchy_el in self.hierarchy:
            content = hierarchy_el.text + '/'
            tmp = [content+i for i in tmp_list]
        return tmp    
        
    
    def set_breadcrumbs(self, value):
        self.__elem_crumbs[self.depth] = value
        self.__elem_crumbs[self.depth+1:] = ['']*(20-self.depth-1)
        self.__crumbs.append('/'.join([e for e in self.__elem_crumbs if e]))



def main():
    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/tmp.html")
    with open(abs_path, 'r') as f:
        html = BeautifulSoup(f, 'lxml')
        
        hierarchy_statement = []
        syntax_statement = []
        if html.select_one("body > #app") is not None:
            new_breadcrumbs = NewJuniperBreadcrumbs(html)
            new_breadcrumbs.create()
        else:
            pass
        

           
        # breadcrumbs = Breadcrumbs(syntax_statement, hierarchy_statement)
        # breadcrumbs_list = breadcrumbs.get_breadcrumbs()
        # full_list = breadcrumbs.add_hierarchy(breadcrumbs_list)
        # print(full_list)

if __name__ == "__main__":
    main()
    
    # print('{} is depth {}'.format(value, depth))