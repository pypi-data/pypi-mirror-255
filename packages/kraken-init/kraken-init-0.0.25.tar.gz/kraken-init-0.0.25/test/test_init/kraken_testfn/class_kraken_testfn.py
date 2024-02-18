
    
import copy
from test.test_init.kraken_testfn.helpers import json
import os
import pkg_resources
from test.test_init.kraken_testfn import kraken_testfn as m

"""
Notes:
To access files in data directory, use:
new_path = pkg_resources.resource_filename('test.test_init.kraken_testfn', old_path)

"""
import uuid
class Testfn:
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
        
        Testfn._objects.append(self)    # Add itself to list of objects instances

        self._id = str(uuid.uuid4())
        self._record = {}
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
        return True

        
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
        

    