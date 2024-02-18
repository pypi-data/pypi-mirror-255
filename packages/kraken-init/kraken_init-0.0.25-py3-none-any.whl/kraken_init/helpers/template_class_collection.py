


def get_filename(name):

    
    return f'{name}/class_{name}s.py'

def get_content(name, directory=None):
    """
    """
    name = f'{name}'
    
    class_name = name.replace('kraken_', '')
    
    class_name = class_name.capitalize()

    class_name_collection = class_name + 's'

    record_value = []

    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir
    
    content = f'''
    
import copy
from {dir}{name}.helpers import json
import os
from {dir}{name} import {name} as m
from {dir}{name}.class_{name} import {class_name}
import pkg_resources


"""
Notes:
To access files in data directory, use:
new_path = pkg_resources.resource_filename('{name}', old_path)

"""

class {class_name_collection}:
    """
    Collection contains many objects

    Args:
        arg1 (str): The arg is used for...
        arg2 (str): The arg is used for...
        arg3 (str): The arg is used for...

    Attributes:
        record (dict): This is where we store attributes
        json (str): Record in json format
        
    """

    def __init__(self):
        self._records = {record_value}
        self._index = 0
        

    def __str__(self):
        """
        """
        return str(self._records)


    def __iter__(self):
        """Defines itself as an iterator
        """
        self._index=0
        return self

    def __next__(self):
        """
        """
        if self._index < len(self._records):
            item = self._records[self._index]
            self._index += 1
            return item
            
        else: 
            self._index = 0
            raise StopIteration

    
    def __repr__(self):
        """
        """
        return str(self._records)

    def __len__(self):
        return len(self._records)
    
    def __eq__(self, other):
        """
        """
        if type(self) != type(other):
            return False
            
        if self._records == other._records:
            return True
        return False
        
    def set(self, values):
        """
        """
        values = values if isinstance(values, list) else [values]
        for i in values:
            self._records.append(i)
        return True

    
    def get(self, property):
        """
        """
        return 

    
    def load(self, values):
        """
        """
        values = values if isinstance(values, list) else [values]
        for i in values:
            o = {class_name}()
            o.load(i)
            self._records.append(o)

        return True


    def dump(self): 
        """
        """
        records = []
        for i in self._records:
            records.append(i.dump())
        return records
        

    def set_json(self, value):
        """
        """
        record = json.loads(value)
        self.load(record)
        return True

    def get_json(self):
        """
        """
        return json.dumps(self.dump())

    @property
    def records(self):
        return self.dump()

    @records.setter
    def records(self, value):
        return self.load(value)
    
    @property
    def json(self):
        return self.get_json()

    @json.setter
    def json(self, value):
        return self.set_json(value)
        

    '''
    
    return content
    