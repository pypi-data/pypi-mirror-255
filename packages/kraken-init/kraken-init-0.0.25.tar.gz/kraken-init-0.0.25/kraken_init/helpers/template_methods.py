import uuid
import datetime

def get_filename(name):

    return f'{name}/{name}.py'

def get_content(name, directory=None):
    """
    """
    class_name = name.replace('kraken_', '')
    
    class_name = class_name.capitalize()


    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir
    
    record_value = {}

    content = f'''
    
import copy
from {dir}{name}.helpers import json
from {dir}{name}.helpers import things
import os
import pkg_resources
import datetime



"""
Notes:
To access files in data directory, use:
new_path = pkg_resources.resource_filename('{name}', old_path)

"""

        
def method1():
    """
    """
    
    return True


def method2():
    """
    """
    
    return True


    
    '''
    
    return content
    