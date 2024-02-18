


def get_filename(name):

    
    return f'{name}/class_{name}.py'

def get_content(name, directory):
    """
    """
    
    class_name = name.replace('kraken_', '')
    
    class_name = class_name.capitalize()

    record_value = {}
    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir
    
    content = f'''
    
import copy
import uuid
import os
import pkg_resources
from {dir}{name}.helpers import json
from {dir}{name} import {name} as m

"""
Notes:
To access files in data directory, use:
new_path = pkg_resources.resource_filename('{dir}{name}', old_path)

"""

class {class_name}:
    """
    The Vehicle object contains a lot of vehicles

    Args:
        arg1 (str): The arg is used for...
        arg2 (str): The arg is used for...
        arg3 (str): The arg is used for...

    Attributes:
        _objects: List of all objects initialized with this class
        record (dict): This is where we store attributes
        json (str): Record in json format
        
    """

    _objects = []    # Initialize array to store all objects instances

    def __init__(self):
        
        {class_name}._objects.append(self)    # Add itself to list of objects instances

        self._id = str(uuid.uuid4())
        self._record = {record_value}
        self._index = 0

    def __str__(self):
        """
        """
        return str(self._record)

    
    def __repr__(self):
        """
        """
        return str(self._record)

    def __iter__(self):
        """ Allows the object to be used in a for loop as a array of only itself
        """
        self._index=0
        return self

    def __next__(self):
        if self._index == 0:
            self._index = 1
            return self
        else:
            self._index = 0
            raise StopIteration


    
    def __eq__(self, other):
        """
        """
        if type(self) != type(other):
            return False
            
        if self._record == other._record:
            return True
        return False

    def __gt__(self, other):
        """
        """
        criteria1 = self.get('startTime')
        criteria2 = other.get('startTime')

        if criteria1 and not criteria2:
            return True

        if not criteria1 and criteria2:
            return True

        if not criteria1 and not criteria2:
            return False

        return criteria1 > criteria2

        
    def set(self, property, value):
        """
        """
        self._record[property] = value
        return True

    
    def get(self, property):
        """
        """
        return self._record.get(property, None)

    
    def load(self, value):
        """
        """
        self._record = value
        return True


    def dump(self): 
        """
        """
        return copy.deepcopy(self._record)
        

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
    def record(self):
        return self.dump()

    @record.setter
    def record(self, value):
        return self.load(value)
    
    @property
    def json(self):
        return self.get_json()

    @json.setter
    def json(self, value):
        return self.set_json(value)
        

    '''
    
    return content
    