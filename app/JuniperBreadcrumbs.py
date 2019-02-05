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
        self.syntaxStatement = self.createSyntaxStatement()
        self.hierarhyStatement = self.createHierarhyStatement()
     
    def get_breadcrumbs(self):
        for stm in self.syntaxStatement:
            if stm.is_match():
                pass
            else if tmp:

    
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
        mylist = [newSyntaxStatement(statement_el) for statement_el in self.syntax]
        return mylist
    
    def createHierarhyStatement(self):
        return newSyntaxStatement(self.hierarchy)
        
class OldJuniperBreadcrumbs(JuniperBreadcrumbs):
    def find_all_statement(self, parameter):
        pass

    def createSyntaxStatement(self):
        pass



class Statement(object):
    
    @property
    def depth(self):
        # statement getter
        return self.__depth
    
    @depth.setter
    def depth(self, depth):
        # statement setter
        self.__depth = depth

    def __init__(self, statement):
        self.statement = self.clean(statement)
  
    def clean(self, param):
        raise NotImplementedError
class newSyntaxStatement(Statement):

    # def __init__(self, level, name):
    # super(Statement, self).__init__(level)
    # self.name = name

    def is_header(self):
        header = re.match(r'^(\w[0-9a-zA-Z-_]+)', self.statement)
        return bool(header)

    def split(self):
        splitlist = [i for i in re.split(r'\s+|\[|\]', self.statement) if i]
        return splitlist

    def is_match(self):
        rematch = re.search(r'(\(|\||\[)', self.statement)
        return bool(rematch)

    def clean(self, param):
        pattern = re.compile(r'(\n\s+|\n)')
        string = pattern.sub(' ', param.text)
        substitutions = {' {': '', ';': ''}
        return self.replace(string, substitutions)

    def set_depth(self):
        self.depth = 0
        if ("ind-statement" in self.statement.get('class')):
            self.depth += 1 
        upper_parent = self.statement.parent
        while (upper_parent.name != 'sw-code'):
            self.depth += 1      
            upper_parent = upper_parent.parent
        return self.depth
    
    def replace(self, string, substitutions):
        substrings = sorted(substitutions, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))
        return regex.sub(lambda match: substitutions[match.group(0)], string)