#!/usr/local/bin/python3
import re
          

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
    
    @property
    def merge_list(self):
        # statement getter
        return self.__merge_list
    
    @merge_list.setter
    def merge_list(self, merge_list):
        # statement setter
        self.__merge_list = merge_list

    def __init__(self, html):
        self.html = html

    def merge(self):
        self.merge_list = []
        if self.hierarchy is not None:
            if self.hierarchy.hierarhy_pathlist:
                for h in self.hierarchy.hierarhy_pathlist:
                    for s in self.syntax.syntax_pathlist:
                        self.merge_list.append("{}/{}".format(h, s))
        elif self.syntax is not None:
            for s in self.syntax.syntax_pathlist:
                self.merge_list.append(s)
        else:
            return None       
        return self.merge_list
      
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

      
    @property
    def syntax_line(self):
        # statement getter
        return self.__syntax_line
    
    @syntax_line.setter
    def syntax_line(self, syntax_line):
        # statement setter
        self.__syntax_line = syntax_line
    
    @property
    def hierarchy_line(self):
        # statement getter
        return self.__hierarchy_line

    @hierarchy_line.setter
    def hierarchy_line(self, hierarchy_line):
        # statement setter
        self.__hierarchy_line = hierarchy_line
    
    def __init__(self, html):
        super().__init__(html)
        self.tag_p = False
        self.syntax_line = []
        self.hierarchy_line = []

    def __add_to_statementList(self, e):
        statementList = [i for i in e.select('.statement')]
        return statementList
    
    def get_current_headers(self, name):
        headers = self.html.select('#topic-content h4')
        for h4 in headers:
            if h4.text.find(name) > -1:
                if (h4.find_next_sibling().name == 'div') and (h4.find_next_sibling()['class'][0] == 'example'):
                    yield h4
                elif h4.find_next_sibling().select('.example'):
                    yield h4
                elif h4.find_next_sibling().name == 'p':
                    yield h4 

    def find_all_statement(self, name):
        current_headers_gen = self.get_current_headers(name)
        length = len(list(current_headers_gen))
        for h4 in self.html.select('#topic-content h4'):
            if length != 0:
                if h4.text.find(name) > -1:                  
                    if (h4.find_next_sibling().name == 'div') and (h4.find_next_sibling()['class'][0] == 'example'):
                        for e in self.html.find_all('div', class_='example'):
                            for i in e.find_previous_siblings("h4", limit=1):
                                if i.text.find(name) > -1:
                                    statementList = self.__add_to_statementList(e)
                                    if name == 'Syntax':
                                        obj = newSyntaxStatement()
                                        obj.statementlist = [i for i in statementList]
                                        self.syntax_line.append(obj)
                                    elif name == 'Hierarchy Level':
                                        obj = newHierarhyStatement()
                                        obj.statementlist = statementList
                                        self.syntax_line.append(obj)
                        length = 0
                    elif h4.find_next_sibling().select('.example'):
                        statementList = []
                        for e in h4.find_next_sibling().select('.example'):
                            statementList = self.__add_to_statementList(e)
                        obj.statementlist = statementList
                        self.syntax_line.append(obj)
                        length = 0
                    elif h4.find_next_sibling().name == 'p':
                        tag_p = True
                        statementList = []
                        for siblings in h4.find_next_siblings():
                            if not (siblings.name == 'h4'):
                                if siblings.name == 'p':
                                    statementList.append(siblings)
                            else:
                                break 
                        obj.tag_p = tag_p
                        obj.statementlist = statementList
                        self.syntax_line.append(obj)
                        length = 0
            else:
               return self.syntax_line
        return self.syntax_line
    

    def createSyntaxStatement(self):
        self.syntax_line = self.find_all_statement('Syntax')
        if self.syntax_line:
            self.syntax = [i for i in self.syntax_line]
            return self.syntax
        else:
            self.syntax = None
            return self.syntax
        
    
    def createHierarhyStatement(self):
        self.hierarchy_line = self.find_all_statement('Hierarchy Level')
        if self.hierarchy_line:
            return self.hierarchy
        else:
            return self.hierarchy
            
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
    def syntax_pathlist(self):
        return self.__syntax_pathlist
    
    @property
    def hierarhy_pathlist(self):
        return self.__hierarhy_pathlist

    def __init__(self, tag_p = False):
        self.tag_p = tag_p
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

    @property
    def tag_p(self):
        # statement getter
        return self.__tag_p

    @tag_p.setter
    def tag_p(self, tag_p):
        # statement setter
        self.__tag_p = tag_p


    @property
    def statementlist(self):
        return self.__statementlist

    @statementlist.setter
    def statementlist(self, statementlist):
        self.__statementlist = statementlist
  
    def get_breadcrumbs(self):
        for el in self.statementlist:
            brackets_match =  self.__get_value_between_brackets(el)
            if brackets_match is not None:
                list_attribute = self.__create_list_from_attribute(brackets_match)
                if isinstance(list_attribute, list):
                    for attribute in list_attribute:
                        mygenerator = self.__createGenerator(attribute, el)
                        self.hierarhy_pathlist.append('/'.join([e for e in mygenerator]))
                elif isinstance(list_attribute, str):
                    mygenerator = self.__createGenerator(list_attribute, el)
                    self.hierarhy_pathlist.append('/'.join([e for e in mygenerator]))
        return self.hierarhy_pathlist

    
    def __createGenerator(self, string, el):
        a = list()
        for val in self.split(string):
            if self.is_var_list(val, el):
                a = a[:-1] + ["{} {}".format(y, val) for x, y in enumerate(a[-1:], start=1)]
            else:
                a.append(val)
        return a
    
    def __create_list_from_attribute(self, brackets_match):
        match = self.__get_atribute_value(brackets_match)
        if match:
            string_wo_comment, match_wo_comment = self.__deleteComment(match, brackets_match)
            if match_wo_comment:
                tmp_string = re.sub('[(|)]', '',  brackets_match if not string_wo_comment else string_wo_comment)
                ttl = 1
                hierarhyList = list()
                for v in match_wo_comment:
                    splitlist = [str(s).strip() for s in re.split(r'\|', v) if s]
                    if not hierarhyList:
                        for s in splitlist:
                            # regex = r'|'.join(map(r'(?<=\s)({})(?=\s|$)'.format, [v for i, v in enumerate(splitlist) if v != s]))
                            regex = [r'(?<=\s)({})(?=\s|$)'.format(re.escape(v)) for i, v in enumerate(splitlist) if v != s]
                            hierarhyList.append(re.sub(r'\s{2,}', ' ', self.__createString(regex, tmp_string, ttl).strip()))         
                        ttl = ttl+1            
                    else:
                        tmp = [i for i in hierarhyList]
                        for s in splitlist:
                            regex = [r'(?<=\s)({})(?=\s|$)'.format(v) for v in splitlist if v != s]
                            for val_el in tmp:
                                hierarhyList.append(re.sub(r'\s{2,}', ' ', self.__createString(regex, val_el, ttl).strip()))
                        del hierarhyList[:len(tmp)]
                        ttl = ttl+1
                return hierarhyList
            else:
                return str(string_wo_comment)
        else:
            return str(brackets_match)
    
    def __get_atribute_value(self, string):
        pattern1 = re.compile(r'\((.*?)\)')    
        match = pattern1.findall(string)
        return match
    
    def __createString(self, regex, init_string, ttl):
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

    def __deleteComment(self, match_list, string):
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

    def is_var_list(self, val, var_list):
        for var in var_list.select('var'):
            if var.text.strip() == val:
                return True
        return False
    
    def split(self, param):
        splitlist = [i for i in re.split(r'\s+', param) if i]
        return splitlist

    def __get_value_between_brackets(self, param):
        result = re.sub(r'(\xa0|\n)', ' ', param.text)
        match =  re.search(r'(?<=\[)(.*)(?=\])', result)
        if match is not None:
            return match.group(0)
        else:
            # no value between [ and ] brackets"
            return None
            # substitutions = {'[': '', ',': '', ']': '',}
            # return self.replace(result, substitutions)

        
class newSyntaxStatement(StatementList):

    @property
    def depth(self):
        # statement getter
        return self.__depth
    
    @depth.setter
    def depth(self, depth):
        # statement setter
        self.__depth = depth

    @property
    def statementlist(self):
        return self.__statementlist

    @statementlist.setter
    def statementlist(self, statementlist):
        self.__statementlist = statementlist
    
    @property
    def tag_p(self):
        # statement getter
        return self.__tag_p

    @tag_p.setter
    def tag_p(self, tag_p):
        # statement setter
        self.__tag_p = tag_p

    
    def __init__(self):
        super().__init__()
        self.statementlist = []
        self.elem_crumbs = ['']*20

    # def __init__(self, level, name):
    # super(Statement, self).__init__(level)
    # self.name = name
  

    def get_command_depth_path(self, value):
        self.elem_crumbs[self.depth] = value
        self.elem_crumbs[self.depth+1:] = ['']*(20-self.depth-1)
        return str('/'.join([e for e in self.elem_crumbs if e]))

    def get_breadcrumbs(self):
        for statement_element in self.statementlist:
            self.set_depth(statement_element)
            cleaned_statement = self.clean(statement_element)
            if re.match(r'^}', cleaned_statement) is None:
                depth_path = self.get_command_depth_path(cleaned_statement)
                command_list = self.__get_all_command_from_path(depth_path)
                if isinstance(command_list, list):
                    for cl_element in command_list:
                        self.syntax_pathlist.append(cl_element)
                elif isinstance(command_list, str):
                    self.syntax_pathlist.append(command_list)
        return self.syntax_pathlist
        
    def __get_all_command_from_path(self, string):
        cercalBracket = re.compile(r'(?<=\()(?:[^)(]|\((?:[^)(]|\([^)(]*\))*\))*(?=\))')
        squareBracket = re.compile(r'(?<=\[)(.*?)(?=\])')
        triangleBracket = re.compile(r'(?<=\<)(.*?)(?=\>)')
        quote = re.compile(r'"(.*?)"')
        comment = re.compile(r'\(([A-Z].[^)(]*?)\)')

        patterns_list = [
            cercalBracket,
            squareBracket,
            triangleBracket
        ]
              
        attributes = []
        if comment.search(string):
            string = comment.sub('', string)
        try:
            for patern_element in patterns_list:
                if patern_element.search(string):
                    if not attributes:
                        atribute_list = self.get_atribute_list(patern_element, string)
                        if atribute_list:
                             attributes.append(string)
                        else:
                            attributes = [attr for attr in atribute_list]
                    else:
                        new_arr = []
                        for target in attributes:
                            for attr in self.get_atribute_list(patern_element, target):
                                if attr:
                                    new_arr.append(attr)
                        if new_arr:
                            attributes = new_arr
                        else:
                            attributes = arr
        except re.error as exception_object:
            print("Unexpected exception: ", exception_object)

        return attributes if attributes else string

    def get_atribute_list(self, patern, string):
        matches = patern.finditer(string)
        length = len(list(matches))  
        tmp = []
        i = 0
        while i < length:
            if not tmp:
                for matchNum, match in enumerate(patern.finditer(string), start=0):
                    if matchNum == i:
                        for s in self.separate_atribute(match, string):
                            tmp.append(s)
            else:
                hh = []
                for t in tmp:
                    for matchNum, match in enumerate(patern.finditer(t), start=0):
                        if matchNum == i:
                            for s in self.separate_atribute(match, t):
                                hh.append(s)
                    
                tmp = hh
            i += 1
        return tmp


    def separate_atribute(self, m, init_string):
        quoteSeparator = re.compile(r'"(.*?)"')
        spaceSeparator = re.compile(r'\s+')
        vlineSeparator = re.compile(r'\|')
        if quoteSeparator.search(m.group()):
            string_generator = self.createStringGenerator(init_string, quoteSeparator, m)
            for line in string_generator:
                yield line
        else:
            if vlineSeparator.search(m.group()):
                string_generator = self.createStringGenerator(init_string, vlineSeparator, m)
                for line in string_generator:
                    yield line
            elif spaceSeparator.search(m.group()):
                string_generator = self.createStringGenerator(init_string, spaceSeparator, m)
                for line in string_generator:
                    yield line
            else:
                # if between bracket one value
                pass

    def createStringGenerator(self, string, separator, match):
        splitlist = [s for s in separator.split(match.group()) if s]
        for s in splitlist:
            s_wo_space = s.strip()
            if s_wo_space is not '':
                yield (string[:match.start()] + s_wo_space + string[match.end():])

    def set_depth(self, statement_element):
        if self.tag_p:
            self.depth = 1
        else:
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

