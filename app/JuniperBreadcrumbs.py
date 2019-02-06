#!/usr/local/bin/python3
import re

class JuniperBreadcrumbs(object):

    __hierarchy_statement = []
    __syntax_statement = []

    @property
    def syntax(self):
        # statement getter
        return self.__syntax_statement
    
    @syntax.setter
    def syntax(self, syntax):
        # statement setter
        self.__syntax_statement = syntax
    
    @property
    def hierarchy(self):
        # statement getter
        return self.__hierarchy_statement
    
    @hierarchy.setter
    def hierarchy(self, hierarchy):
        # statement setter
        self.__hierarchy_statement = hierarchy

    def __init__(self, html):
        self.hierarchy = self.find_all_statement('Hierarchy Level', html)
        self.syntax = self.find_all_statement('Syntax', html)
       
    def find_all_statement(self, parameter, html):
        return AttributeError('Not Implemented')
    
    def createSyntaxStatement(self):
        """
        Фабричный Метод
        """
        raise AttributeError('Not Implemented')

class NewJuniperBreadcrumbs(JuniperBreadcrumbs):
       
    def find_all_statement(self, parameter, html):
        target_list = []
        for e in html.find_all('div', class_='example'):
            for i in e.find_previous_siblings("h4", limit=1):
                if i.text.find(parameter) > -1:
                    if len(target_list) > 0:
                        target_list.extend([i for i in e.select('.statement')])
                    else:
                        target_list = [i for i in e.select('.statement')]
        return target_list
    
    def createSyntaxStatement(self):
        return newSyntaxStatement(self.syntax)
    
    def createHierarhyStatement(self):
        return newHierarhyStatement(self.hierarchy)
        
class OldJuniperBreadcrumbs(JuniperBreadcrumbs):
    def find_all_statement(self, parameter):
        pass

    def createSyntaxStatement(self):
        pass

class StatementList(object):

    __pathlist = list()
    
    @property
    def statementlist(self):
        return self.__statementlist

    @statementlist.setter
    def statementlist(self, statementlist):
        self.__statementlist = statementlist
    
    @property
    def pathlist(self):
        return self.__pathlist

    def __init__(self, statementlist):
        self.__statementlist = statementlist


    def get_breadcrumbs(self):
        raise NotImplementedError

class newHierarhyStatement(StatementList):
    def get_breadcrumbs(self):
        for el in self.statementlist:
            var_el = el.select('var')
            clean_el  = self.clean(el)
            for i in self.split(clean_el):
                print(i)
            # el_text = el.text.replace(u'\xa0|\\n', ' ')
            # print(el_text)
            # el_list = self.split(el.text)

    def clean(self, param):
        pattern = re.compile(r'(\xa0|\n)')
        return pattern.sub(' ', param.text)
    
    def split(self, param):
        splitlist = [i for i in re.split(r'\s+', param) if i]
        return splitlist
class newSyntaxStatement(StatementList):

    __elem_crumbs = ['']*20

    @property
    def depth(self):
        # statement getter
        return self.__depth
    
    @depth.setter
    def depth(self, depth):
        # statement setter
        self.__depth = depth


    # def __init__(self, level, name):
    # super(Statement, self).__init__(level)
    # self.name = name

    def get_breadcrumbs(self):
        for statement_element in self.statementlist:
            self.set_depth(statement_element)
            cleaned_statement = self.clean(statement_element)
            if self.is_match(cleaned_statement):
                if self.is_header(cleaned_statement):
                    for index, value in enumerate(self.split(cleaned_statement), 1):
                        if (index == 2):
                            self.depth += 1
                        self.set_breadcrumbs(value)
                else:
                    for index, value in enumerate(self.split(cleaned_statement), 1):
                        self.set_breadcrumbs(value)
                continue
            elif re.match(r'^}', cleaned_statement) is None:
                self.set_breadcrumbs(cleaned_statement)
        return self.pathlist 

    def set_breadcrumbs(self, value):
        self.__elem_crumbs[self.depth] = value
        self.__elem_crumbs[self.depth+1:] = ['']*(20-self.depth-1)
        self.pathlist.append('/'.join([e for e in self.__elem_crumbs if e]))

    def is_header(self, statement):
        header = re.match(r'^(\w[0-9a-zA-Z-_]+)', statement)
        return bool(header)

    def split(self, statement):
        splitlist = [i for i in re.split(r'\s+|\[|\]', statement) if i]
        return splitlist

    def is_match(self, statement):
        rematch = re.search(r'(\(|\||\[)', statement)
        return bool(rematch)

    def clean(self, param):
        pattern = re.compile(r'(\n\s+|\n)')
        string = pattern.sub(' ', param.text)
        substitutions = {' {': '', ';': ''}
        return self.replace(string, substitutions)

    def set_depth(self, statement_element):
        self.depth = 0
        if ("ind-statement" in statement_element.get('class')):
            self.depth += 1 
        upper_parent = statement_element.parent
        while (upper_parent.name != 'sw-code'):
            self.depth += 1      
            upper_parent = upper_parent.parent
        return self.depth
    
    def replace(self, string, substitutions):
        substrings = sorted(substitutions, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))
        return regex.sub(lambda match: substitutions[match.group(0)], string)