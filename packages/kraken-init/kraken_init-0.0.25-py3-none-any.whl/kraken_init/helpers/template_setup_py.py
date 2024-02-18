
def get_filename(name):

    return 'setup.py'

def get_content(name, directory=None):


    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir

    
    title = name.replace('_', '-')
    git_name = name.replace('_', '')
    package_data = '{"": ["data/*.db", "data/*.csv", "data/*.zip"]}'
    content = f'''
import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="{title}",
    version="0.0.1",
    description="{title}",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tactik8/{git_name}",
    author="Tactik8",
    author_email="info@tactik8.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={package_data},
    install_requires=["kraken-thing", "requests", "flask", "flask-login", "kraken-user"],

)

    '''
    return content