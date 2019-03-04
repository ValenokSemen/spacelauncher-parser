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
    
    def __init__(self, html):
        self.html = html
        self.syntax = []
        self.hierarchy = []

      
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
   
  
    def __init__(self, html):
        super().__init__(html)
   
    def find_all_statement(self, name):
        headers = self.html.select('#topic-content h4')
        for h4 in headers:
            if h4.text.find(name) > -1:
               yield from self.get_html_statement_after_h4(h4, name)
  
    def get_html_statement_after_h4(self, h4, name):
        for sibling in h4.find_next_siblings():
            if not (sibling.name == 'h4'):
                if sibling.select('.example'):
                    sibling_list = []
                    for e in sibling.select('.example'):
                            if sibling_list:
                                sibling_list.extend([i for i in e.select('.statement')])
                            else:
                                sibling_list = [i for i in e.select('.statement')]
                    obj = None
                    if name == 'Syntax':
                        obj = newSyntax()
                    elif name == 'Hierarchy Level':
                        obj = HierarhyStatement()
                    obj.statementlist = [i for i in sibling_list]
                    yield obj
                elif (sibling.name == 'div') and (sibling['class'][0] == 'example'):
                    sibling_list = []
                    sibling_list = [i for i in sibling.select('.statement')]
                    obj = None
                    if name == 'Syntax':
                        obj = newSyntax()
                    elif name == 'Hierarchy Level':
                        obj = HierarhyStatement()
                    obj.statementlist = [i for i in sibling_list]
                    yield obj
                elif sibling.name == 'p':
                    tag_p = True
                    obj = None
                    if name == 'Syntax':
                        obj = newSyntax(tag_p)
                    elif name == 'Hierarchy Level':
                        obj = HierarhyStatement()
                    obj.statementlist.append(sibling)
                    yield obj
            else:
                break
    
    def createSyntaxStatement(self):
        self.syntax = self.find_all_statement('Syntax')
        if self.syntax:
            return self.syntax
        else:
            self.syntax = None
            return self.syntax
        
    
    def createHierarhyStatement(self):
        self.hierarchy = self.find_all_statement('Hierarchy Level')
        if self.hierarchy:
            return self.hierarchy
        else:
            self.hierarchy = None
            return self.hierarchy


    def get_syntax_pathlist(self):
        if self.syntax:
            for s in self.syntax:
                if s.get_breadcrumbs():
                    for s_path in s.syntax_pathlist:
                        yield s_path
    
    def get_hierarchy_pathlist(self):
        if self.hierarchy:
            for h in self.hierarchy:
                if h.get_breadcrumbs():
                    for h_path in h.hierarhy_pathlist:
                        yield h_path

    def merge_statement(self):
        syntax_pathlist = [i for i in self.get_syntax_pathlist()]
        hierarchy_pathlist = [i for i in self.get_hierarchy_pathlist()]
        if self.hierarchy is not None:
            for h_path in hierarchy_pathlist:
                for s_path in syntax_pathlist:
                    yield "{}/{}".format(h_path, s_path)
        elif self.syntax is not None:
             for s_path in syntax_pathlist:
                yield s_path
        else:
            return None
        
class OldJuniperBreadcrumbs(JuniperBreadcrumbs):
      
    def find_all_statement(self, name):
        headers = self.html.select('#topic-content h4')
        for h4 in headers:
            if h4.text.find(name) > -1:
               yield from self.get_html_statement_after_h4(h4, name)

    def get_html_statement_after_h4(self, h4, name):
         for sibling in h4.find_next_siblings():
            if not (sibling.name == 'h4'):
                if sibling.select('.example'):
                    sibling_list = []
                    for e in sibling.select('.example'):
                            if sibling_list:
                                sibling_list.extend([i for i in e.select('.ExampleInline') if len(list(i.select(i.name))) == 0])
                            else:
                                sibling_list = [i for i in e.select('.ExampleInline') if len(list(i.select(i.name))) == 0]
                    obj = None
                    if name == 'Syntax':
                        obj = oldSyntax()
                    elif name == 'Hierarchy Level':
                        obj = HierarhyStatement()
                    obj.statementlist = [i for i in sibling_list]
                    yield obj
                elif sibling.name == 'p':
                    tag_p = True
                    obj = None
                    if name == 'Syntax':
                        obj = oldSyntax(tag_p)
                    elif name == 'Hierarchy Level':
                        obj = HierarhyStatement()
                    obj.statementlist.append(sibling)
                    yield obj
            else:
                break


    def createSyntaxStatement(self):
        self.syntax = self.find_all_statement('Syntax')
        return self.syntax

    def createHierarhyStatement(self):
        self.hierarchy =  self.find_all_statement('Hierarchy Level')
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

    def __init__(self):
        self.__syntax_pathlist = []
        self.__hierarhy_pathlist = []

    def get_breadcrumbs(self):
        raise NotImplementedError

    def clean(self, param):
        pattern_newline = re.compile(r'(\n\s+|\n)')
        pattern_dots = re.compile(r'(\.{2,})')
        
        string = param.text
        if pattern_newline.search(string):
            string = pattern_newline.sub(' ', string)

        if pattern_dots.search(string):
            string = pattern_dots.sub(' ', string)
        
        substitutions = {'{': '', ';': ''}
        return self.replace(string, substitutions)
   
    def replace(self, string, substitutions):
        substrings = sorted(substitutions, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))
        return regex.sub(lambda match: substitutions[match.group(0)], string).strip()

class SyntaxStatement(StatementList):

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
        self.elem_crumbs = ['']*20


    def get_command_depth_path(self, value):
        self.elem_crumbs[self.depth] = value
        self.elem_crumbs[self.depth+1:] = ['']*(20-self.depth-1)
        return str('/'.join([e for e in self.elem_crumbs if e]))

    def get_breadcrumbs(self):
        for statement_element in self.statementlist:
            self.set_depth(statement_element)
            cleaned_statement = self.clean(statement_element)
            # if string is empty
            if cleaned_statement:
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
                            attributes = [attr for attr in atribute_list]
                        else:
                            attributes.append(string)
                    else:
                        new_arr = []
                        for target in attributes:
                            for attr in self.get_atribute_list(patern_element, target):
                                if attr:
                                    new_arr.append(attr)
                        if new_arr:
                            attributes = new_arr
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


    def set_depth(self, parameter_list):
        raise NotImplementedError

class newSyntax(SyntaxStatement):
    def __init__(self, tag_p = False):
        super().__init__()
        self.tag_p = tag_p
        self.statementlist = []

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

class oldSyntax(SyntaxStatement):
    def __init__(self, tag_p = False):
        super().__init__()
        self.tag_p = tag_p
        self.statementlist = []
    
    def set_depth(self, statement_element):
        if self.tag_p:
            self.depth = 1
        else:
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

class HierarhyStatement(StatementList):

    @property
    def statementlist(self):
        return self.__statementlist

    @statementlist.setter
    def statementlist(self, statementlist):
        self.__statementlist = statementlist

    def __init__(self, tag_p = False):
        super().__init__()
        self.statementlist = []
  
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

