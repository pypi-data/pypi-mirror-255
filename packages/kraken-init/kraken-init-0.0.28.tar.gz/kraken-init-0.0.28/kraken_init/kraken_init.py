
import os
from kraken_init.helpers import template_class
from kraken_init.helpers import template_class_collection
from kraken_init.helpers import template_license_txt
from kraken_init.helpers import template_readme_md
from kraken_init.helpers import template_setup_cfg
from kraken_init.helpers import template_setup_py
from kraken_init.helpers import template_dockerfile
from kraken_init.helpers import template_tests
from kraken_init.helpers import template_git_ignore
from kraken_init.helpers import template_main
from kraken_init.helpers import template_requirements
from kraken_init.helpers import template_init
from kraken_init.helpers import template_helper_json
from kraken_init.helpers import template_helper_things
from kraken_init.helpers import template_flask
from kraken_init.helpers import template_methods





def init(name, force=True, directory=None):
    """
    Parameters:
        name: name of the package (kraken_something)
        force: repalces files if True
        directory: if specified, creates package in given directory instead of /
    """

    # Create init if directory
    if directory:
        d = []
        for i in directory.split('/'):
            d.append(i)
            filename = '__init__.py'
            write_to_file(filename, '', force, '/'.join(d))

    
    # Create __init__
    filename = f'{name}/helpers/__init__.py'
    content = ''
    write_to_file(filename, content, force, directory)

    # Create files
    filename = template_methods.get_filename(name)
    content = template_methods.get_content(name, directory)
    write_to_file(filename, content, force, directory)
    
    # Create files
    filename = template_class.get_filename(name)
    content = template_class.get_content(name, directory)
    write_to_file(filename, content, force, directory)

    # Create files
    filename = template_class_collection.get_filename(name)
    content = template_class_collection.get_content(name, directory)
    write_to_file(filename, content, force, directory)
    
    # Create files
    filename = template_license_txt.get_filename(name)
    content = template_license_txt.get_content(name, directory)
    write_to_file(filename, content, force, directory)
    
    # Create files
    filename = template_readme_md.get_filename(name)
    content = template_readme_md.get_content(name, directory)
    write_to_file(filename, content, force, directory)
    
    # Create files
    filename = template_setup_cfg.get_filename(name)
    content = template_setup_cfg.get_content(name, directory)
    write_to_file(filename, content, force, directory)
    
    # Create files
    filename = template_setup_py.get_filename(name)
    content = template_setup_py.get_content(name, directory)
    write_to_file(filename, content, force, directory)


    # Create files
    filename = template_dockerfile.get_filename(name)
    content = template_dockerfile.get_content(name, directory)
    write_to_file(filename, content, force, directory)

    # Create files
    filename = template_tests.get_filename(name)
    content = template_tests.get_content(name, directory)
    write_to_file(filename, content, force, directory)

    # Create files
    filename = template_git_ignore.get_filename(name)
    content = template_git_ignore.get_content(name, directory)
    write_to_file(filename, content, force, directory)

    # Create files
    filename = template_requirements.get_filename(name)
    content = template_requirements.get_content(name, directory)
    write_to_file(filename, content, force, directory)

    # Create files
    filename = template_init.get_filename(name)
    content = template_init.get_content(name, directory)
    write_to_file(filename, content, force, directory)

    # Create files
    filename = template_helper_json.get_filename(name)
    content = template_helper_json.get_content(name, directory)
    write_to_file(filename, content, force, directory)

    # Create files
    filename = template_helper_things.get_filename(name)
    content = template_helper_things.get_content(name, directory)
    write_to_file(filename, content, force, directory)
    
    # Create files
    filename = template_flask.get_filename(name)
    content = template_flask.get_content(name, directory)
    write_to_file(filename, content, force, directory)

    
    # Create main
    filename = template_main.get_filename(name)
    original_content = read_file(filename)
    new_content = template_main.get_content(name, directory)
    content = new_content + '\n' + original_content
    content = content.replace('kraken_init.init', '#kraken_init.init')
    write_to_file(filename, content, force, directory)

    return 


def write_to_file(filename, content, force=False, directory=None):
    """
    """

    if directory and directory != '': 
        filename = directory + '/' + filename


    
    
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    except:
        a=1

    if os.path.exists(filename) and force == False:
        print(f'File {filename} already exists')
        return
        
    with open(filename, 'w', newline='') as f:
        f.write(content)
    return

def read_file(filename):
    """
    """

    with open(filename, 'r', newline='') as f:
        content = f.read()
    return content