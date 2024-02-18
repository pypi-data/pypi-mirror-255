

def get_filename(name):

    return f'requirements.txt'


def get_content(name=None, directory=None):
    """
    """

    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir

    
    content = f'''
requests
kraken-thing
flask
flask-login
kraken-user
gunicorn


    
    '''
    return content