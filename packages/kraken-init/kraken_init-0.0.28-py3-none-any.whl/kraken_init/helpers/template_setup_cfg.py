

def get_filename(name):

    return f'setup.cfg'



def get_content(name, directory=None):

    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir

    
    content = '''
    # Inside of setup.cfg
[metadata]
description-file = README.md

    '''
    return content