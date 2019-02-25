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
                id=target_list.id,
                metadata=target_list.metadata,
                path=target_list.path,
                software=target_list.software,
                title=target_list.title,
                commandPath=target_list.commandPath,
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
        self.commandPath = []


    def getPath(self):
        return self.path

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
                breadcrumbs = NewJuniperBreadcrumbs(htmlData)
            else:
                breadcrumbs = OldJuniperBreadcrumbs(htmlData)
            breadcrumbs.createSyntaxStatement().get_breadcrumbs()
            breadcrumbs.createHierarhyStatement().get_breadcrumbs()
        self.commandPath =  breadcrumbs.merge()
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
    # command = JuniperService()
    # sem = asyncio.Semaphore(6)
    # loop = asyncio.get_event_loop()
    # f = [commandlist(cl, sem) for cl in command.getCommandList()]
    # loop.run_until_complete(wait_with_progress(f))
    # with open('juniper-command-plus.json', 'w', encoding='utf-8') as outfile:
    #     outfile.write(command.pretty_print())
    #     #add trailing newline for POSIX compatibility
    #     outfile.write('\n')

    rel_path = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(rel_path, "test_files/tmp.html")

    with open(abs_path, 'r') as html_file:
        html = BeautifulSoup(html_file, 'lxml')               
        if html.select_one("body > #app") is not None:
            new_breadcrumbs = NewJuniperBreadcrumbs(html)
            new_breadcrumbs.createSyntaxStatement()
            new_breadcrumbs.createHierarhyStatement()
            tmp = new_breadcrumbs.merge()
            print('\n'.join(tmp))
        else:
            new_breadcrumbs = OldJuniperBreadcrumbs(html)
            new_breadcrumbs.createSyntaxStatement()
            new_breadcrumbs.createHierarhyStatement()
            tmp = new_breadcrumbs.merge()
            print('\n'.join(tmp))
    # start_string = 'edit protocols mstp interface (all | interface-name)'
    # match = is_match(start_string)
    # if match:
    #     hierarhyList = list()
    #     string_wo_comment, match_wo_comment = deleteComment(match, start_string)
    #     if match_wo_comment:
    #         tmp_string = re.sub('[(|)]', '',  start_string if not string_wo_comment else string_wo_comment)
    #         ttl = 1
    #         for v in match_wo_comment:
    #             splitlist = [str(s).strip() for s in re.split(r'\|', v) if s]
    #             if not hierarhyList:
    #                 for s in splitlist:
    #                     # regex = r'|'.join(map(r'(?<=\s)({})(?=\s|$)'.format, [v for i, v in enumerate(splitlist) if v != s]))
    #                     regex = [r'(?<=\s)({})(?=\s|$)'.format(v) for i, v in enumerate(splitlist) if v != s]
    #                     hierarhyList.append(re.sub(r'\s{2,}', ' ', createString(regex, tmp_string, ttl).strip()))         
    #                 ttl = ttl+1            
    #             else:
    #                 tmp = [i for i in hierarhyList]
    #                 for s in splitlist:
    #                     regex = [r'(?<=\s)({})(?=\s|$)'.format(v) for i, v in enumerate(splitlist) if v != s]
    #                     for val_el in tmp:
    #                         hierarhyList.append(re.sub(r'\s{2,}', ' ', createString(regex, val_el, ttl).strip()))
    #                 del hierarhyList[:len(tmp)]
    #                 ttl = ttl+1
    #     else:
    #         hierarhyList.append(string_wo_comment)
    #     print('\n'.join(hierarhyList))
    # else:
    #     print(start_string)

def is_match(string):
    pattern1 = re.compile(r'\((.*?)\)')    
    match = pattern1.findall(string)
    return match

def createString(regex, init_string, ttl):
    tmpstr = ''
    for el in regex:
        matches = [v for v in re.finditer(el, init_string if not tmpstr else tmpstr , re.MULTILINE)]
        if tmpstr == '':
            for matchNum, match in enumerate(matches, start=1):
                if (len(matches) > 1) and (matchNum == ttl):
                    tmpstr = init_string[:match.start()] + init_string[match.end():]
                    break
                elif (len(matches) == 1):
                    tmpstr = init_string[:match.start()] + init_string[match.end():]
                    break
        else:
            for matchNum, match in enumerate(matches, start=1):
                if (len(matches) > 1) and (matchNum == ttl):
                    tmpstr = tmpstr[:match.start()] + tmpstr[match.end():]
                    break
                elif (len(matches) == 1):
                    tmpstr = tmpstr[:match.start()] + tmpstr[match.end():]
                    break
    return tmpstr

def deleteComment(match_list, string):
    new_str = ''
    new_matchList = []
    for match in match_list:
        split_arr = [str(s).strip() for s in re.split(r'\|', match) if s]
        if len(split_arr) == 1:
            if new_str == '':
                new_str =  re.sub(r'\(({})\)'.format(match), '', string)
            else:
                new_str =  re.sub(r'\(({})\)'.format(match), '', new_str)
        else:
            new_matchList.append(match)
    new_str =  re.sub(r'\s{2,}', ' ', new_str).strip()
    return new_str, new_matchList

if __name__ == "__main__":
    main()


    # print('{} is depth {}'.format(value, depth))
