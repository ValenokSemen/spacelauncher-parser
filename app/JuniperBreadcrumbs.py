#!/usr/local/bin/python3
import re

class ListOfStatement(object):
    __list_name = ''
    __statementList_statement = list()

   
    @property
    def is_tag_p(self):
        # statement getter
        return self.__is_tag_p

    @is_tag_p.setter
    def is_tag_p(self, tag_p=False):
        # statement setter
        self.__is_tag_p = tag_p
    
    @property
    def statementList(self):
        # statement getter
        return self.__statementList_statement
    
    @statementList.setter
    def statementList(self, statementList):
        # statement setter
        self.__statementList_statement = statementList

    def __init__(self, name, html):
        self.__list_name = name
        self.is_tag_p = False
        self.html = html
        self.statementList = self.find_all_statement()

    def __add_to_statementList(self, e):
        if len(self.statementList) > 0:
            self.statementList.extend([i for i in e.select('.statement')])
        else:
            self.statementList = [i for i in e.select('.statement')]
    
    def find_all_statement(self):
        for h4 in self.html.select('#topic-content h4'):
            if h4.text.find(self.__list_name) > -1:                  
                if (h4.find_next_sibling().name == 'div') and (h4.find_next_sibling()['class'][0] == 'example'):
                    for e in self.html.find_all('div', class_='example'):
                        for i in e.find_previous_siblings("h4", limit=1):
                            if i.text.find(self.__list_name) > -1:
                                self.__add_to_statementList(e)
                elif h4.find_next_sibling().select('.example'):
                    for e in h4.find_next_sibling().select('.example'):
                        self.__add_to_statementList(e)
                else:
                    for siblings in h4.find_next_siblings():
                        if not re.search(r'h4', siblings.name):
                            self.statementList.append(siblings)
                        else:
                            self.is_tag_p = True
                            break
        return self.statementList
                

class JuniperBreadcrumbs(object):

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
        self.html = html
        self.syntax = self.createSyntaxStatement()
        self.hierarchy = self.createHierarhyStatement()


    def merge(self):
        merge_list = list()
        for h in self.hierarchy.hierarhy_pathlist:
           for s in self.syntax.syntax_pathlist:
               merge_list.append("{}/{}".format(h, s))
        return merge_list
      
    def createSyntaxStatement(self):
        """
        Фабричный Метод
        """
        raise NotImplementedError
    
    def createHierarhyStatement(self):
        """
        Фабричный Метод
        """
        raise NotImplementedError

class NewJuniperBreadcrumbs(JuniperBreadcrumbs):
    
    def createSyntaxStatement(self):
        return newSyntaxStatement(ListOfStatement('Syntax', self.html))
    
    def createHierarhyStatement(self):
        return newHierarhyStatement(ListOfStatement('Hierarchy Level', self.html))
        
class OldJuniperBreadcrumbs(JuniperBreadcrumbs):
    
    def find_all_statement(self, parameter, html):
        target_list = []
        for target in html.find_all('div', id='topic-content'):
            after_h4_links = [i.find_next_sibling() for i in target.select('h4') if i.text.find(parameter) > -1]
            for example_div in after_h4_links:
                if len(target_list) > 0:
                    target_list.extend([i for i in example_div.select('.ExampleInline') if len(list(i.select(i.name))) == 0])
                else:
                    target_list = [i for i in example_div.select('.ExampleInline') if len(list(i.select(i.name))) == 0]
        return target_list

    def createSyntaxStatement(self):
        self.syntax =  oldSyntaxStatement(self.syntax_list)
        return self.syntax

    def createHierarhyStatement(self):
        self.hierarchy =  oldHierarhyStatement(self.hierarchy_list)
        return self.hierarchy

class StatementList(object):

    __syntax_pathlist = list()
    __hierarhy_pathlist = list()
    
    @property
    def statementlist(self):
        return self.__statementlist

    @statementlist.setter
    def statementlist(self, statementlist):
        self.__statementlist = statementlist
    
    @property
    def syntax_pathlist(self):
        return self.__syntax_pathlist
    
    @property
    def hierarhy_pathlist(self):
        return self.__hierarhy_pathlist

    def __init__(self, statementlist, is_p_statementlist = False):
        self.__statementlist = statementlist
        self.__syntax_pathlist = []
        self.__hierarhy_pathlist = []



    def get_breadcrumbs(self):
        raise NotImplementedError

    def clean(self, param):
        pattern = re.compile(r'(\n\s+|\n)')
        #add delete whitespace from start and end
        string = pattern.sub(' ', param.text).strip()
        substitutions = {' {': '', ';': ''}
        return self.replace(string, substitutions)

    def replace(self, string, substitutions):
        substrings = sorted(substitutions, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))
        return regex.sub(lambda match: substitutions[match.group(0)], string)

class newHierarhyStatement(StatementList):
    
    def get_breadcrumbs(self):
        for el in self.statementlist:
            a = list()
            for val in self.split(self.clean(el)):
                if self.is_var_list(val, el):
                    a = a[:-1] + ["{} {}".format(y, val) for x, y in enumerate(a[-1:], start=1)]
                else:
                    a.append(val)
            self.hierarhy_pathlist.append('/'.join([e for e in a]))
        return self.hierarhy_pathlist

    def is_var_list(self, val, var_list):
        for var in var_list.select('var'):
            if var.text == val:
                return True
        return False
    
    def split(self, param):
        splitlist = [i for i in re.split(r'\s+', param) if i]
        return splitlist

    def clean(self, param):
        result = re.sub(r'(\xa0|\n)', ' ', param.text)
        match =  re.search(r'(?<=\[)(.*)(?=\])', result)
        if match is not None:
            return match.group(0)
        else:
            substitutions = {'[': '', ',': '', ']': '',}
            return self.replace(result, substitutions)

        
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
        return self.syntax_pathlist 

    def set_breadcrumbs(self, value):
        self.__elem_crumbs[self.depth] = value
        self.__elem_crumbs[self.depth+1:] = ['']*(20-self.depth-1)
        self.syntax_pathlist.append('/'.join([e for e in self.__elem_crumbs if e]))

    def is_header(self, statement):
        if re.match(r'^(\w[0-9a-zA-Z-_]+)', statement):
            if re.search(r'(\(|\[)', statement):
                return True
            else:
                return False

    def split(self, statement):
        splitlist = [i for i in re.split(r'\s+|\[|\]|\||\(|\)', statement) if i]
        return splitlist

    def is_match(self, statement):
        rematch = re.search(r'(\(|\||\[)', statement)
        return bool(rematch)

    def set_depth(self, statement_element):
        self.depth = 0
        if ("ind-statement" in statement_element.get('class')):
            self.depth += 1 
        upper_parent = statement_element.parent
        while (upper_parent.name != 'sw-code'):
            self.depth += 1      
            upper_parent = upper_parent.parent
        return self.depth
    

class oldSyntaxStatement(StatementList):

    __elem_crumbs = ['']*20

    @property
    def depth(self):
        # statement getter
        return self.__depth
    
    @depth.setter
    def depth(self, depth):
        # statement setter
        self.__depth = depth

    def set_depth(self, statement_element):
        self.depth = 0
        pattern = re.compile(r'margin-left: 30pt;')
        if pattern.search(statement_element['style']):
            self.depth += 1
        upper_parent = statement_element.parent
        while self.to_end(upper_parent):
            self.depth += 1
            upper_parent = upper_parent.parent
        return self.depth
    

    def to_end(self, param):
        if param.get('class') is None:
            return True
        if re.search(r'example', param['class'][0]):
            return False
        else:
            return True

    def is_match(self, statement):
        rematch = re.search(r'(\(|\||\[)', statement)
        return bool(rematch)

    def is_header(self, statement):
        if re.match(r'^(\w[0-9a-zA-Z-_]+)', statement):
            if re.search(r'(\(|\[)', statement):
                return True
            else:
                return False
            
    def get_breadcrumbs(self):
        for element in self.statementlist:
            self.set_depth(element)
            cleaned_statement = self.clean(element)
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
        return self.syntax_pathlist 

    def split(self, statement):
        splitlist = [i for i in re.split(r'\s+|\[|\]|\||\(|\)', statement) if i]
        return splitlist
    
    def set_breadcrumbs(self, value):
        self.__elem_crumbs[self.depth] = value
        self.__elem_crumbs[self.depth+1:] = ['']*(20-self.depth-1)
        self.syntax_pathlist.append('/'.join([e for e in self.__elem_crumbs if e]))


class oldHierarhyStatement(StatementList):
    def get_breadcrumbs(self):
        for el in self.statementlist:
            a = list()
            for val in self.split(self.clean(el)):
                if self.is_var_list(val, el):
                    a = a[:-1] + ["{} {}".format(y, val) for x, y in enumerate(a[-1:], start=1)]
                else:
                    a.append(val)
            self.hierarhy_pathlist.append('/'.join([e for e in a]))
        return self.hierarhy_pathlist

    def is_var_list(self, val, var_list):
        for var in var_list.select('i'):
            if var.text == val:
                return True
        return False
    
    def split(self, param):
        splitlist = [i for i in re.split(r'\s+', param) if i]
        return splitlist

    def clean(self, param):
        result = re.sub(r'(\xa0|\n)', ' ', param.text)
        match =  re.search(r'(?<=\[)(.*)(?=\])', result)
        if match is not None:
            return match.group(0)
        else:
            substitutions = {'[': '', ',': '', ']': '',}
            return self.replace(result, substitutions)

