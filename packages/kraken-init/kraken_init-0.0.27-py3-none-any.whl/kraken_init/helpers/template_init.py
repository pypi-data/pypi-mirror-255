

def get_filename(name):

    return f'{name}/__init__.py'


def get_content(name=None, directory=None):
    """
    """

    class_name = name.replace('kraken_', '')

    class_name = class_name.capitalize()
    class_name_collection = class_name + 's'

    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir

    
    content = f'''
from {dir}{name} import {name}
from {dir}{name}.class_{name} import {class_name}
from {dir}{name}.class_{name + 's'} import {class_name_collection}
    '''
    return content