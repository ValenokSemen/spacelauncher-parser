import json
import os.path
import re
import sys
from contextlib import closing

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException

from juniperbreadcrumbs import NewJuniperBreadcrumbs, OldJuniperBreadcrumbs

from sqlalchemy.ext.mutable import Mutable


# https://github.com/pkolt/design_patterns/blob/master/generating/builder.py
# https://www.giacomodebidda.com/factory-method-and-abstract-factory-in-python/
# https://www.juniper.net/documentation/en_US/junos/topics/reference/configuration-statement/aggregated-ether-options-interfaces-ex-series.html
# https://github.com/Patreon/patreon-python/blob/master/patreon/jsonapi/parser.py
# https://www.dev2qa.com/python-json-dump-to-or-load-from-file-example/


try:
    import ptvsd
    ptvsd.enable_attach(address=('0.0.0.0', 5678), redirect_output=True)
    ptvsd.wait_for_attach()
    print('ptvsd is started')
except:
    print('ptvsd not working')

class RestResponseObj(Mutable, object):
    __parent__ = None

    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, dict) and not isinstance(value, RestObject):
            return RestObject(value)
        elif isinstance(value, list) and not isinstance(value, RestList):
            return RestList(value)
        else:
            return value

    def changed(self):
        if self.__parent__:
            self.__parent__.changed()
        else:
            super().changed()

    def __call__(self):
        return json.loads(json.dumps(self))

class RestObject(RestResponseObj, dict):
    def __init__(self, data, parent=None):
        if not isinstance(data, dict):
            raise ValueError('RestObject data must be dict object')
        self.__data__ = {}
        self.__parent__ = parent
        for k, v in data.items():
            self.__data__[k] = self.__init_data(v)
    
    def __init_data(self, v):
        if isinstance(v, dict) and not isinstance(v, RestObject):
            return RestObject(v, parent=self)
        elif isinstance(v, list) and not isinstance(v, RestList):
            return RestList(v, parent=self)
        return v

class RestList(RestResponseObj, list):
    def __init__(self, data, parent=None):
        if not isinstance(data, list):
            raise ValueError('RestList data must be list object')

        self.__parent__ = parent

        for item in data:
            self.append(item)


    @property
    def __data__(self):
        return json.loads(self.pretty_print())

    def pretty_print(self, indent=4):
        return json.dumps(self, indent=indent)

    def __repr__(self):
        return super(RestList, self).__repr__()

    def __getitem__(self, index):
        item = super(RestList, self).__getitem__(index)
        return item

    def __iter__(self):
        for item in list.__iter__(self):
                yield item

    
    def append(self, item):
        super(RestList, self).append(ResponseJson.parse(item, parent=self))
        self.changed()

    def extend(self, items):
        for item in items:
            self.append(item)

    def insert(self, index, item):
        if isinstance(item, RestResponseObj):
            super(RestList, self).insert(index, ResponseJson.parse(item, parent=self))
            self.changed()

    def pop(self, index=None):
        if index:
            value = super(RestList, self).pop(index)
        else:
            value = super(RestList, self).pop()
        self.changed()
        return value

    def remove(self, item):
        super(RestList, self).remove(item)
        self.changed()

class ResponseJson(object):
    
    def __new__(self, data):
        if isinstance(data, str):
            return ResponseJson.load(data)
        else:
            return ResponseJson.parse(data)

    @staticmethod
    def parse(data, parent=None):
        if isinstance(data, dict):
            return RestObject(data, parent=parent)
        elif isinstance(data, list):
            return RestList(data, parent=parent)
        elif isinstance(data, type(None)):
            return RestObject({}, parent=parent)
        else:
            return data

    @staticmethod
    def load(data):
        try:
            data = json.loads(data)
        except Exception:
            raise ValueError('Data must be JSON deserializable')
        
        return ResponseJson.parse(data) 

def main():
    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/old_tmp.html")
    with open(abs_path, 'r') as html_file:
        html = BeautifulSoup(html_file, 'lxml')
        with open('/app/juniper-command.json', 'r') as file:
                tmp = ResponseJson.load(file.read())
                print(tmp[0])
        
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
