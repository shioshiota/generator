import numbers
import random
import string
import sys
import yaml

class Case:

    map = {}

    def calc_formula(self, formula):
        result = 0
        for members in str(formula).split('+'):
            member = members.split('-')
            for i in range(len(member)):
                n = 0
                if self.map.has_key(member[i]):
                    n = self.map[member[i]]
                elif member[i] == '':
                    n = 0
                else:
                    n = int(member[i])
                if i == 0:
                    result += n
                else:
                    result -= n
        return result

    def calc(self, r):
        if str(r).find(',') == -1:
            return self.calc_formula(r)
        t = r[1:-1].split(',')
        lower = self.calc_formula(t[0])
        upper = self.calc_formula(t[1])
        return random.uniform(lower, upper)

    def random_integer(self, item):
        result = int(self.calc(item['range']))
        if item.has_key('name'):
            self.map[str(item['name'])] = result
        return str(result)

    def random_decimal(self, item):
        format = '{0:.' + str(item['precision']) + 'f}'
        return str.format(format, self.calc(item['range']))

    def random_string(self, item):
        length = int(self.calc(item['length']))
        source = ''
        case = {
            'lowercase' : string.lowercase,
            'uppercase' : string.uppercase,
            'digit' : string.digits
            }
        for letter in item['letter']:
            source += case[letter]
        return "".join([random.choice(source) for x in xrange(length)])

    def random_enum(self, item):
        values = item['value']
        return str(values[random.randint(0, len(values) - 1)])

    def parse_item(self, item):
        if item['type'] == 'integer':
            return self.random_integer(item)
        elif item['type'] == 'decimal':
            return self.random_decimal(item)
        elif item['type'] == 'string':
            return self.random_string(item)
        elif item['type'] == 'enum':
            return self.random_enum(item)
        elif isinstance(item['type'], list):
            result = ''
            for data in item['type']:
                result += self.parse_data(data)
            return result

    def parse_data(self, data):
        delimiter = {
            'none': '',
            'new_line': '\n',
            'space': ' ',
            'comma': ',',
            'piriod': '.',
            'hyphen': '-',
            'underscore': '_',
            'colon': ':',
            'semicolon': ';'
            }
        result = ''
        if data.has_key('repeat'):
            s = set()
            l = []
            repeat = self.calc(data['repeat'])
            for i in range(repeat):
                if data.has_key('option') and ('unique' in data['option']):
                    while True:
                        r = self.parse_item(data)
                        if r not in s:
                            l.append(r)
                            s.add(r)
                            break
                else:
                    l.append(self.parse_item(data))
            if data.has_key('option'):
                if 'asc' in data['option']:
                    l.sort();
                elif 'desc' in data['option']:
                    l.sort(reverse=True)
            for i in range(repeat):
                if 0 < i:
                    if data.has_key('separator'):
                        result += delimiter[data['separator']]
                result += l[i]
        else:
            result = self.parse_item(data)
        if data.has_key('delimiter'):
            return result + delimiter[data['delimiter']]
        return result

def parse_case(case):
    if isinstance(case, list):
        input = ''
        for item in case:
            input += parse_case(item)
        return input
    else:
        return Case().parse_data(case)

def parse(data):
    format = data['format']
    filename = data['filename']
    for i in range(data['repeat']):
        input = filename.split('.', 1)[0] + str(i) + '.' + filename.split('.', 1)[1]
        open(input, 'w').write(parse_case(format))

random.seed(0)
file = open(sys.argv[1]).read()
alldata = yaml.load(file)
if isinstance(alldata, list):
    for data in alldata:
        parse(data)
else:
    parse(alldata)
