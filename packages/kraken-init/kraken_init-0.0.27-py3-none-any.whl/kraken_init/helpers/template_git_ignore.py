
def get_filename(name):

    return f'.gitignore'


def get_content(name, directory=None):
    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir

    
    content = '''
poetry.lock
pyproject.toml


    '''
    return content