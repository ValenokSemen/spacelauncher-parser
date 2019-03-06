import re

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
                if hh:    
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
    __pattern = re.compile(r'\(([A-Z].[^)(]*?)\)')

    def handle(self, content):
        content = self.__pattern.sub('', content)
        return content
  
    def get_pattern(self):
        return self.__pattern

class TriangleBracket(Handler):
    """Обработчик для <>"""
    __pattern = re.compile(r'(?<=\<)(?:[^><]|\((?:[^><]|\([^><]*\))*\))*(?=\>)')

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

class SquareBracket(Handler):
    """Обработчик для []"""
    __pattern = re.compile(r'(?<=\[)(.*?)(?=\])')

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