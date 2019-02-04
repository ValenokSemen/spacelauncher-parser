class JuniperBreadcrumbs(object):

    __hierarchy_statement = []
    __syntax_statement = []

    def __init__(self, html):
        self.__hierarchy_statement = self.find_all_statement('Hierarchy Level', html)
        self.__syntax_statement = self.find_all_statement('Syntax', html)
    
    def find_all_statement(self, parameter, html):
        """
        Фабричный Метод
        """
        return AttributeError('Not Implemented')
    
    def create(self):
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
    
    def create(self):
        pass
        
class OldJuniperBreadcrumbs(JuniperBreadcrumbs):
    def find_all_statement(self, parameter):
        pass

    def create(self):
        pass
