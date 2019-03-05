import json
import os.path
import re
import sys
from contextlib import closing
import tqdm
import aiohttp
import asyncio


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


class GenericJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            pass
        cls = type(obj)
        result = {
            '__custom__': True,
            '__module__': cls.__module__,
            '__name__': cls.__name__,
            'data': obj.__dict__ if not hasattr(cls, '__json_encode__') else obj.__json_encode__
        }
        return result

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
        self.datasource = Request()
        self.command_obj_list = self.initCommandList()

    def initCommandList(self):
        raise NotImplementedError

class JuniperService(JuniperCommand):
    
    def getCommandList(self):
        return self.command_obj_list
    
    def initCommandList(self):
        commandList = self.datasource.getJsonFromUrl()
        command_obj_list = []
        if isinstance(commandList, list):
             for index, commanditems in enumerate(commandList, start=1):
                if isinstance(commanditems, dict):
                     for target_list in commanditems['cl']:
                         command_obj_list.append(Command(target_list ,self))
                if index == 6:
                    break
        return command_obj_list

    def pretty_print(self, indent=4):
        schema = list()
        for target_list in self.getCommandList():
            schema.append(dict(
                id=target_list.getId(),
                metadata=target_list.getMetadata(),
                path=target_list.getPath(),
                software=target_list.getSoftware(),
                title=target_list.getTitle(),
                page=target_list.getPage(),
                commandPath=target_list.getCommandPath(),
            ))
        return json.dumps(schema, cls=GenericJSONEncoder, indent=indent)


class Command(object):
    def __init__(self, target, document):
        self.document = document
        self.id = target['id']
        self.metadata = target['metadata']
        self.path = target['path']
        self.software = target['software']
        self.title = target['title']
        self.page = ''
        self.commandPath = []


    def getPath(self):
        return self.path
    
    def getPage(self):
        return self.page

    def getMetadata(self):
        return self.metadata

    def getId(self):
        return self.id

    def getSoftware(self):
        return self.software
    
    def getTitle(self):
        return self.title

    def getCommandPath(self):
        return self.commandPath

    def setCommandPath(self, html):
        breadcrumbs = None
        if html is not None:
            htmlData = BeautifulSoup(html, 'lxml')
            if htmlData.select_one("body > #app") is not None:
                self.page = 'new'
                breadcrumbs = NewJuniperBreadcrumbs(htmlData)
                breadcrumbs.createSyntaxStatement()
                breadcrumbs.createHierarhyStatement()
                self.commandPath = [i for i in breadcrumbs.merge_statement()]
            else:
                self.page = 'old'
                breadcrumbs = OldJuniperBreadcrumbs(htmlData)
                breadcrumbs.createSyntaxStatement()
                breadcrumbs.createHierarhyStatement()
                self.commandPath = [i for i in breadcrumbs.merge_statement()]
        return self.getCommandPath()


async def get_url(*args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(*args, **kwargs) as resp:
            return await resp.text()


def add_cl(query, page):
    query.setCommandPath(page)


async def commandlist(query, sem):
    url = query.path
    with await sem:
        page = await get_url(url, compress=True)
    add_cl(query, page)

async def wait_with_progress(coros):
    for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
        await f
 


def main():
    command = JuniperService()
    sem = asyncio.Semaphore(6)
    loop = asyncio.get_event_loop()
    f = [commandlist(cl, sem) for cl in command.getCommandList()]
    loop.run_until_complete(wait_with_progress(f))
    with open('juniper-command-plus.json', 'w', encoding='utf-8') as outfile:
        outfile.write(command.pretty_print())
        #add trailing newline for POSIX compatibility
        outfile.write('\n')

def test():
    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/tmp.html")

    with open(abs_path, 'r') as html_file:
        html = BeautifulSoup(html_file, 'lxml')               
        if html.select_one("body > #app") is not None:
            breadcrumbs = NewJuniperBreadcrumbs(html)
            syntax = breadcrumbs.createSyntaxStatement()
            hierarhy = breadcrumbs.createHierarhyStatement()                   
            print('\n'.join(breadcrumbs.merge_statement()))     
        else:
            breadcrumbs = OldJuniperBreadcrumbs(html)
            syntax = breadcrumbs.createSyntaxStatement()
            hierarhy = breadcrumbs.createHierarhyStatement()
            print('\n'.join(breadcrumbs.merge_statement()))
            # if hierarhy is not None:
            #     for h in hierarhy:
            #         if h.get_breadcrumbs():
            #             print('\n'.join(map(str, h.hierarhy_pathlist)))
                                                                     

class Separator(object):
    def get_pattern(self):
        raise NotImplementedError

class VlineSeparator(Separator):
    def get_pattern(self):
        vlineSeparator = re.compile(r'\|')
        return vlineSeparator


class SpaceSeparator(Separator):
    def get_pattern(self):
        spaceSeparator = re.compile(r'\s+')
        return spaceSeparator

class Handler(object):
    """Абстрактный класс обработчика"""

    def __init__(self):
        pass
    
    def atribute_list(self, content):
        tmp = []
        matches = self.get_pattern().finditer(content)
        for i, v in enumerate(matches):
            if not tmp:
                for num, match in enumerate(self.get_pattern().finditer(content), start=0):
                    if num == i:
                        for s in self.separate_atribute(match, content):
                            tmp.append(s)
            else:
                hh = []
                for t in tmp:
                    for matchNum, match in enumerate(self.get_pattern().finditer(t), start=0):
                        if matchNum == i:
                            for s in self.separate_atribute(match, t):
                                hh.append(s)
                    
                tmp = hh
        return tmp
    
    def separate_atribute(self,  m, init_string):
        if self.get_separates():
             for separator in self.get_separates():
                separator_pattern = separator.get_pattern()
                if separator_pattern.search(m.group()):
                    splitlist = [s for s in separator_pattern.split(m.group()) if s]
                    for s in splitlist:
                        s_wo_space = s.strip()
                        if s_wo_space is not '':
                            yield (init_string[:m.start()] + s_wo_space + init_string[m.end():])
                    break
                

    def handle(self, content):
        raise NotImplementedError   

    def get_pattern(self):
        raise NotImplementedError
    
    def get_separates(self):
        raise NotImplementedError
 
class CircleBracket(Handler):
    """Обработчик для ()"""
    __pattern = re.compile(r'(?<=\()(?:[^)(]|\((?:[^)(]|\([^)(]*\))*\))*(?=\))')

    def __init__(self, separates = None):
        super().__init__()
        self.__separates = []
        if separates is not None:
            self.__separates += separates
    
    def get_separates(self):
        return self.__separates
    
    def get_pattern(self):
        return self.__pattern

    def handle(self, content):
        attributes = []
        if isinstance(content, str):
            if not attributes:
                atribute_list = self.atribute_list(content)
                if atribute_list:
                    attributes = [attr for attr in atribute_list]
                else:
                    attributes.append(content)
        elif isinstance(content, list):
            new_arr = []
            for target in content:
              for attr in self.atribute_list(target):
                  if attr:
                      new_arr.append(attr)
            if new_arr:
                attributes = new_arr
        return attributes if attributes else content

class Comment(Handler):
    """Обработчик для удаления комментария"""
    pattern = re.compile(r'\(([A-Z].[^)(]*?)\)')

    def handle(self, content):
        content = self.pattern.sub('', content)
        return content
  
    def get_pattern(self):
        return self.pattern
class TriangleBracket(Handler):
    """Обработчик для <>"""
    __pattern = re.compile(r'(?<=\<)(.*?)(?=\>)')


class ContentFilter(object):
    def __init__(self, filters=None):
        self._filters = []
        if filters is not None:
            self._filters += filters
 
    def filter(self, content):
        initial_string = content
        for filter in self._filters:
            if filter.get_pattern().search(initial_string):
                content = filter.handle(content)
        return content

def run():
    my_array = [
                # 'vlan (vlan-id | vlan-name);',
                # 'file filename <files number> <size test> <world-readable | no-world-readable>;',
                # 'flag flag <flag-modifier> <disable>',
                # 'flag flag <detail | extensive | terse>;',
                # '(no-world-readable | world-readable);',
                # 'arp ip-address (mac | multicast-mac) mac-address <publish> file (notice | verbose) filename (no-world-readable  world-readable)',
                # 'arp ip-address (mac | multicast-mac) mac-address (publish | unpublish) ',
                # '(vrrp-group | vrrp-inet6-group) group-number {',
                # '(cbr rate |rtvbr peak rate sustained rate burst length |vbr peak rate sustained rate burst length);',
                # 'virtual-address [ addresses peak rate sustained];',
                'flag [rtvbr | peak | rate | sustained rate] vrrp-inet6-group',
                'level [all | error | info | notice | verbose | warning]',
                # 'connect-method https|http;',
                # 'connect-method https | http | get | post captive warning-test;',
                # 'authentication-order [dot1x | mac-radius | captive-portal];',
                # 'tcp [port];',
                # 'all <extensive>;',
                # 'allow-commands-regexps [ "regular expression 1" "regular expression 2" .... ]',
                # 'allow-commands "(regular-expression)|(regular-expression1)|(regulare-expression2)..."',
                # 'interface (all | [interface-names])',
                # '(ethernet (Alarm) | management-ethernet) {',
                # "fpcs (NSSU Upgrade Groups) (slot-number | [list-of-slot-numbers]);",
                # "n-plus-n (Power Management);",
                # "ethernet (Aggregated Devices) {"
    ]

    filter = ContentFilter([
                Comment(),
                CircleBracket([VlineSeparator(), SpaceSeparator()])
                ])
    content = "clear bfd (My Tech comment) session <logical-system (all | logical-system-name)>"
    filtered_content = filter.filter(content)
    print(filtered_content)


if __name__ == "__main__":
    # main()
    # test()
    run()
            