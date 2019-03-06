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