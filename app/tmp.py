import json
import os.path
import re
import sys
from contextlib import closing

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
        split_data =  re.split('\s+|\[|\]', self.matchstring)
        self.mylist = [i for i in split_data if i]


def get_depth(element):
    depth = 0
    if ("ind-statement" in element.get('class')):
        depth += 1
    parent = element.parent
    while (parent.name != 'sw-code'):
        depth += 1      
        parent = parent.parent
    return depth


def clean_data(param):
    pattern = re.compile('(\n\s+|\n)')
    return pattern.sub(' ', param).replace(' {', '')

def is_split_data(value):
    match = re.search(r'(\(|\||\[)', value) 
    return bool(match)

def set_split_data(value):
    match = re.search(r'^(\w[0-9a-zA-Z-_]+)|(\[.*?\])|(\(.*?\))', value) 

    if match.group(0):
        pass

    # if match:
    #     return re.split('\s+|\[|\]', match[0])     

if __name__ == "__main__":
    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/tmp.html")
    with open(abs_path, 'r') as f:
        html = BeautifulSoup(f, 'lxml')
        get_syntax = html.select_one("sw-code")
        crumbs = []
        elem_crumbs = ['']*20
        for index, value in enumerate(get_syntax.select(".statement"), 1):
            depth = get_depth(value)
            value = clean_data(value.text)
            
            m = Rematcher(value)
            if m.is_match(r'(\(|\||\[)'):
               m.group(r'^(\w[0-9a-zA-Z-_]+)')
               m.split()
               if m.get_header:
                   for i, v in enumerate(m.mylist, 1):
                       if (i == 2):
                           depth += 1
                       elem_crumbs[depth] = v
                       elem_crumbs[depth+1:] = ['']*(20-depth-1)
                       crumbs.append('/'.join([e for e in elem_crumbs if e])) 
               else:
                   for i, arg in enumerate(m.mylist, 1):
                       elem_crumbs[depth] = arg
                       elem_crumbs[depth+1:] = ['']*(20-depth-1)
                       crumbs.append('/'.join([e for e in elem_crumbs if e]))
               continue
            
            if re.match(r'^}', value) is None:
                elem_crumbs[depth] = value
                elem_crumbs[depth+1:] = ['']*(20-depth-1)
                crumbs.append('/'.join([e for e in elem_crumbs if e]))
                
#                 # print('{} is depth {}'.format(value, depth))