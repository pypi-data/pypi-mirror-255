

def get_filename(name):

    return f'main.py'


def get_content(name, directory=None):
    """
    """
    
    class_name = name.replace('kraken_', '')
    class_name = class_name.capitalize()
    git_name = name.replace('_', '')
    class_name_collection = class_name + 's'


    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir
    
    content = f'''
import os
from {dir}{name} import {name}
from {dir}{name} import {class_name}
from {dir}{name} import {class_name_collection}
from {dir}{name} import flask_routes

"""
Project structure created by kraken_init

To dos
1. Configure pypi package publishing
- Todo: Configure github pypi publish action - DONE 
- Todo: Create pypi token (https://pypi.org/manage/account/)
- Todo: Add pypi api token to github secret (https://github.com/tactik8/{git_name}/settings/secrets/actions)
- Change pypi script "on" (trigger) to: 
    on:
      push:
        branches:
          - 'main'

2. Configure google cloud
- Todo: Create new cloud run service (https://console.cloud.google.com/run?project=kraken-v2-369412)

3. Add packages 
- Todo: Add required packages to setup.py
- Todo: Add required packages to requirements.txt
"""

def test():
    """Perform tests
    """
    os.system("pip install pytest")
    os.system("python -m pytest {name}* -vv")

# To run unit tests on package, uncomment the following line:
#test()

# To enable the flask api, uncomment the following line:
#flask_routes.run_api()

# To use classes, uncomment the following lines:
#{class_name.lower()} = {class_name}()
#{class_name_collection.lower()} = {class_name_collection}()

    '''
    return content