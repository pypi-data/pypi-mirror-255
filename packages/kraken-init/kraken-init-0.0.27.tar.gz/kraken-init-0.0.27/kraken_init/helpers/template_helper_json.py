
def get_filename(name):

    return f'{name}/helpers/json.py'


def get_content(name, directory=None):


    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir
    
    content = '''
import json
import datetime
import os

""" JSON
"""
def _default_json(obj):

    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj:
            new_obj[key] = _default_json(value)
    elif isinstance(obj, list):
        new_obj = []
        for item in obj:
            new_obj.append(_default_json(item))
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        new_obj = obj.isoformat()
    else:
        new_obj = obj

    return new_obj

def _convert_string_to_dates(record):

    if isinstance(record, dict):
        new_record = {}
        for key, value in record.items():
            new_record[key] = _convert_string_to_dates(value)

    elif isinstance(record, list):
        new_record = []
        for item in record:
            new_record.append(_convert_string_to_dates(item))
    else:
        new_record = record
        try:
            if record:
                new_record = datetime.datetime.fromisoformat(record)
        except Exception as e:
            a=1
    return new_record


def dumps(record):
    return json.dumps(record, default=_default_json, indent=4)

def loads(string):
    record = json.loads(string)
    return _convert_string_to_dates(record)

def dump(filename, record):

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename,"w") as fw:
        json.dump(record, fw, default=_default_json, indent=4)


def load(filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename,"r") as fr:
        out_dict = json.load(fr, default=_default_json, indent=4)
    return _convert_string_to_dates(out_dict)



    '''
    return content

