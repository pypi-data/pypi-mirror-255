

def get_filename(name):

    return f'README.md'


def get_content(name=None, directory=None):
    """
    """

    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir

    
    content = f'''
    # {name}
    <definition>


    ## How to use

    ```
    from {dir}{name} import {name}

    

    ```


    
    '''
    return content