import json

class Export(object):
    def export(self, parameter_list):
        raise NotImplementedError

class ExportToJSON(Export):
    def export(self, parameter_list):
        return 'json: name={0}, bleed={1}'.format(parameter_list.name, parameter_list.bleed)

class ExportToXML(Export):
    def export(self, parameter_list):
        return 'xml: name={0}, bleed={1}'.format(parameter_list.name, parameter_list.bleed)


class Pet(object):
    def __init__(self, name):
        self.name = name

class Cat(Pet):
    def __init__(self, name, bleed = None):
        super().__init__(name)
        self.bleed = bleed

class ExCat(Cat):
    def __init__(self, name, bleed = None, export = None):
        super().__init__(name, bleed)
        self._export = export or ExportToXML()
        if not isinstance(self._export, Export):
            raise ValueError('bad export', export)
    
    def export(self):
        return self._export.export(self)


cat = ExCat("Тимоха", "МейнКун")
result = cat.export()
print(result)



class HumanExport(object):
    def save(self, param):
        raise NotImplementedError

class ExToJson(HumanExport):
    def save(self, param):
        param.data['people'].append({'name': param.name, 'surname': param.surname, 'number': param.mobile_number})
        with open(param.file_path, 'w') as f:
            f.seek(0)
            json.dump(param.data, f)

class ExToXml(HumanExport):
    def save(self, param):
        return 'xml: name={0}, bleed={1}'.format(parameter_list.name, parameter_list.bleed)

  
class Creatures:
    def __init__(self, name):
        self.name = name
  
  
class Human(Creatures):
    def __init__(self, name, surname, mobile_number):
        super().__init__(name)
        self.surname = surname
        self.mobile_number = mobile_number
  
  
class Editor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self._get()
  
    def _get(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Ошибка, файл {0} не найден!".format(self.file_path))

class ExEditor(Editor):
    def __init__(self, file_path, employer = None, export = None):
        super().__init__(file_path)
        self.employer = employer
        self._export = export or ExToJson()

    def save(self):
        self._export.save(self)


human = Human("Ivan", "Testov", '79516506401')
exeditor = ExEditor('path', employer = human, export = ExToJson())
exeditor.save()
