import re

class Handler(object):
    """Абстрактный класс обработчика"""
    def handle(self, content):
        raise NotImplementedError()
 
 
class CircleBracket(Handler):
    """Обработчик для ()"""
    __cercalBracket = re.compile(r'(?<=\()(?:[^)(]|\((?:[^)(]|\([^)(]*\))*\))*(?=\))')

    def handle(self, content):
        if content == 404:
            return 'Страница не найдена'
 
class Comment(Handler):
    """Обработчик для удаления комментария"""
    __comment = re.compile(r'\(([A-Z].[^)(]*?)\)')
    
    def handle(self, content):
        if content == 404:
            return 'Страница не найдена'
  
class TriangleBracket(Handler):
    """Обработчик для <>"""
    __triangleBracket = re.compile(r'(?<=\<)(.*?)(?=\>)')

    def handle(self, content):
        if content == 500:
            return 'Ошибка сервера'

class ContentFilter(object):
    def __init__(self, filters=None):
        self._filters = []
        if filters is not None:
            self._filters += filters
 
    def filter(self, content):
        for filter in self._filters:
            content = filter.handle(content)
        return content
 
filter = ContentFilter([
                Comment()
                CircleBracket(),
                TriangleBracket()
                ])
content = "clear bfd session <logical-system (all | logical-system-name)>"
filtered_content = filter.filter(content)