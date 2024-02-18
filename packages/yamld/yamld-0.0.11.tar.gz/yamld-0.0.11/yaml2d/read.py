import pandas as pd
from ast import literal_eval

if __name__ == "__main__":
    from common import Entry, NaN
else:
    from .common import Entry, NaN


class Read():
    FIRST_CHAR2TYPES = {
        '[': list,
        '"': str,
        "'": str,
    }

    LIST_CAST_TYPES = {
        (int, float): float,
        (float, int): float
    }


    def __init__(self, is_onelist=False, tgt_parent=None):
        self.is_onelist = is_onelist
        self.tgt_parent = tgt_parent
        
        #init read
        self.out = None
        self.current_parent = None
        self.list_counter = 0
        self.yaml_obj = dict()
        self.yaml_obj_types = dict()
        self.all_types = dict()
        self.list_counter = 0

        #line state
        self.key = None
        self.value = None
        self.is_parent = False
        self.is_child = False
        self.is_minus = False
        self.is_obj_parsing_done = False
        self.is_parent_value = False
        self.is_obj_parsing = False
        self.is_2ndimen_parsing = False
    
    @classmethod
    def _ylist_type_cast(cls, old_types, new_types):
        def c(fromto):
            from_type, to_type = fromto
            if to_type is type(None):
                return from_type

            if from_type == to_type:
                return from_type
            else:
                new_type =  cls.LIST_CAST_TYPES.get(fromto, False)
                if not new_type:
                    raise Exception(f'List type error, tyring to cast {from_type} to {to_type}')
                return new_type
        
        return map(c, zip(old_types.values(), new_types.values()))

    @classmethod
    def infer_type(cls, value):
        ytype = cls.FIRST_CHAR2TYPES.get(value[0], False)
        if not ytype:
            if value == NaN:
                ytype = type(None)
            else:
                ytype = float if '.' in value else int
        return ytype

    def _reset(self):
        #reset and skip
        if self.is_parent:
            if self.is_onelist and self.list_counter:
                raise Exception("You specified a one list('-') yaml2d file but a key was found after parsing the list")
            if self.is_parent_value:
                self.current_parent = None
            else:
                self.current_parent = self.key
            self.list_counter = 0
            
        if self.is_obj_parsing_done:
            self.yaml_obj = dict()
            self.yaml_obj_types = dict()
            


    def process_line(self, line):
        striped_line = line.strip()
        if not striped_line:
            return None

        self.is_child = line[0].isspace()
        self.is_parent = not self.is_child
        line = striped_line

        key, value = line.strip().split(':', 1)
        self.key, self.value = key.strip(), value.strip()
        
        self.is_parent_value = self.is_parent and self.value

        self.is_minus = key[0] == '-'
        self.is_obj_parsing_done = (self.is_parent or self.is_minus) and bool(self.yaml_obj)
        
        #states
        if self.is_child:
            self.is_obj_parsing = True
        if self.is_parent:
            self.is_obj_parsing = False

        if self.is_obj_parsing:
            self.is_2ndimen_parsing = True
        if self.is_parent:
            self.is_2ndimen_parsing = False
        
        
    def parsing_obj(self):
        #record current line if not parent
        if self.is_minus:
            self.list_counter += 1
            self.key = self.key[1:].strip()
        self.yaml_obj[self.key] = self.value
        ytype = self.infer_type(self.value)        
        self.yaml_obj_types[self.key] = ytype


    def read_obj(self):
        #write previous object to the self.backend if done parsing
        if self.list_counter and self.current_parent in self.all_types:
            new_obj_types = self.all_types[self.current_parent]
            new_obj_types = self._ylist_type_cast(self.all_types[self.current_parent], self.yaml_obj_types)
            self.yaml_obj_types = dict(zip(self.yaml_obj_types.keys(), new_obj_types))
        self.all_types[self.current_parent] = self.yaml_obj_types
        return True


    def read_generator(self, lines):
        for line in lines:
            self.process_line(line)
            if self.is_obj_parsing_done:
                self.read_obj()
                yield Entry(
                    parent=self.current_parent,
                    obj=self.yaml_obj,
                    ytype=self.yaml_obj_types,
                    is_ylist= bool(self.list_counter),
                    is_parent_value= False,
                    is_last=False
                )
            if self.is_parent_value:
                yield Entry(
                    parent= self.key,
                    obj=self.value,
                    ytype= self.infer_type(self.value),
                    is_parent_value= True,
                    is_ylist=False,
                    is_last=False
                )
            self._reset()
            if self.is_obj_parsing:
                self.parsing_obj()
        if self.is_obj_parsing:
            self.read_obj()
            yield Entry(
                obj=self.yaml_obj,
                ytype=self.yaml_obj_types,
                is_ylist= bool(self.list_counter),
                is_parent_value= False,
                is_last=False
            )
            yield Entry(is_last=True)
        

def _python_eval(value):
    if value == NaN:
        return None
    return literal_eval(value)


def read_onelist_meta(lines):
    read = Read(is_onelist=True, tgt_parent=None)
    out = {}
    for entry in read.read_generator(lines):
        if entry.is_ylist:
            return out
        if entry.is_parent_value:
            out[entry.parent] = _python_eval(entry.obj)
        else:
            out[entry.parent] = {k: _python_eval(v) for k, v in entry.obj.items()}
                 

def read_onelist_generator(lines, transform=None):
    read = Read(is_onelist=True, tgt_parent=None)
    def gen():
        for entry in read.read_generator(lines):
            if not entry.is_ylist:
                continue
            tmp = {k: _python_eval(v) for k, v in entry.obj.items()}
            if transform:
                tmp = transform(tmp)
            yield tmp
    return gen()


def read_onelist_dataframe(lines):
    read = Read(is_onelist=True, tgt_parent=None)
    data = {}
    gen = read_onelist_generator(lines)
    for entrydict in gen:
        if not data:
            data = {k:[v] for k,v in entrydict.items()}
        else:
            try:
                for k, v in entrydict.items():
                    data[k].append(v)
            except KeyError as e:
                raise Exception('Probably violated YAML (-)list must contain fixed features: ' + e.message) from e
    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    yamlf = """
config1:
  key1: 'value1'
  key2: 'value2'
  key3: 'value3'

config2:
  keyA: 'valueA'
  keyB: 'valueB'
  keyC: 'valueC'

data:
  - name: 'John Doe'
    age: 30
    city: 'New York'
  - name: 'Jane Smith'
    age: 25
    city: 'San Francisco'
  - name: 'Bob Johnson'
    age: 35
    city: 'Chicago'
  - name: 'Test'
    age: 35.0
    city: 'Chicago'
    """

    out = read_onelist_meta(yamlf.splitlines())
    print(out)
    gen = read_onelist_generator(yamlf.splitlines())

    for item in gen:
        print(item)
