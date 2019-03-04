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
                if index == 4:
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
                self.commandPath = []
        
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
    abs_path = os.path.join(rel_path, "test_files/old_tmp.html")

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
            if syntax is not None:
                for s in syntax:
                    print('\n'.join(map(str, s.get_breadcrumbs())))                     
                               



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
    
    # cercalBracket = re.compile(r'(?<=\()(.*?)(?=\))')
    cercalBracket = re.compile(r'(?<=\()(?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*(?=\))')
    squareBracket = re.compile(r'(?<=\[)(.*?)(?=\])')
    triangleBracket = re.compile(r'(?<=\<)(.*?)(?=\>)')
    quote = re.compile(r'"(.*?)"')

    comment = re.compile(r'\(([A-Z].[^)(]*?)\)')
    
    for target_list in my_array:
        tmplist = []
        if comment.search(target_list):
            target_list = deleteComment(comment, target_list)
        if cercalBracket.search(target_list):
            func_res = my_funcname(cercalBracket, target_list, tmplist)
            if isinstance(func_res, str):
                tmplist.append(func_res)
            elif isinstance(func_res, list):
                tmplist = func_res
        if squareBracket.search(target_list):
            func_res = my_funcname(squareBracket, target_list, tmplist)
            if isinstance(func_res, str):
                tmplist.append(func_res)
            elif isinstance(func_res, list):
                tmplist = func_res
        if triangleBracket.search(target_list):
            func_res = my_funcname(triangleBracket, target_list, tmplist)
            if isinstance(func_res, str):
                tmplist.append(func_res)
            elif isinstance(func_res, list):
                tmplist = func_res
        if quote.search(target_list):
            pass

        if tmplist:
            for t in tmplist:
                print(t)
        else:
            print(target_list)


def deleteComment(patern, string):
    return patern.sub('', string)

def my_funcname(patern, string, arr):
    if not arr:
        arr = [attr for attr in get_atribute_list(patern, string)]
        return arr if arr else string
    else:
        new_arr = []
        for target in arr:
            for attr in get_atribute_list(patern, target):
                if attr:
                    new_arr.append(attr)
        return new_arr if new_arr else arr

def get_atribute_list(patern, string):
    matches = patern.finditer(string)
    length = len(list(matches))  
    tmp = []
    i = 0
    while i < length:
        if not tmp:
            for matchNum, match in enumerate(patern.finditer(string), start=0):
                if matchNum == i:
                    for s in funcname(match, string):
                        tmp.append(s)
        else:
            hh = []
            for t in tmp:
                for matchNum, match in enumerate(patern.finditer(t), start=0):
                    if matchNum == i:
                        for s in funcname(match, t):
                            hh.append(s)
                   
            tmp = hh
        i += 1
    return tmp


def funcname(m, init_string):
    quoteSeparator = re.compile(r'"(.*?)"')
    spaceSeparator = re.compile(r'\s+')
    vlineSeparator = re.compile(r'\|')
    if quoteSeparator.search(m.group()):
        string_generator = createStringGenerator(init_string, quoteSeparator, m)
        for line in string_generator:
            yield line
    else:
        if vlineSeparator.search(m.group()):
            string_generator = createStringGenerator(init_string, vlineSeparator, m)
            for line in string_generator:
                yield line
        elif spaceSeparator.search(m.group()):
            string_generator = createStringGenerator(init_string, spaceSeparator, m)
            for line in string_generator:
                yield line
        else:
            # if between bracket one value
            pass

def createStringGenerator(string, separator, match):
    splitlist = [s for s in separator.split(match.group()) if s]
    for s in splitlist:
        s_wo_space = s.strip()
        if s_wo_space is not '':
             yield (string[:match.start()] + s_wo_space + string[match.end():])
       

if __name__ == "__main__":
    # main()
    test()
    # run()
            