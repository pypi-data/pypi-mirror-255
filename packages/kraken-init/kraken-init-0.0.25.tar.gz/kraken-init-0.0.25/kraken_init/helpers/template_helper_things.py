
import uuid
import datetime

def get_filename(name):

    return f'{name}/helpers/things.py'


def get_content(name, directory=None):


    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir
    
    content = f'''
import datetime


def get_value(key, record):
    """Return value from different types of input records
    Accepts action record, or simple object
    """

    if record.get('@type', None) == 'action':
        record = record.get('object', None)

    value = record.get(key, None)

    return value

def get_instrument_record():
    """
    """
    record = {{
        "@type": "WebAPI",
        "@id": "{str(uuid.uuid4())}",
        "name": "{name}",
        "description": "description"
    }}

    return record

def get_action_record(object_record, result_record=None):
    """
    """

    action_record = {{
        '@type': 'action',
        '@id': str(uuid.uuid4()),
        'name': '{name}',
        'object': object_record,
        'instrument': get_instrument_record(),
        'startTime': datetime.datetime.now(),
        'actionStatus': 'activeActionStatus'
    }}

    if result_record:
        action_record['endTime'] = datetime.datetime.now()
        action_record['actionStatus'] = 'completedActionStatus'
        action_record['result'] = result_record

    return action_record


def log_start(action_record):
    """
    """
    action_record['startTime'] = datetime.datetime.now()
    action_record['actionStatus'] = 'activeActionStatus'
    return action_record


def log_success(action_record):
    """
    """
    action_record['endTime'] = datetime.datetime.now()
    action_record['actionStatus'] = 'completedActionStatus'
    return action_record


def log_error(action_record, error_message=None):
    """
    """
    action_record['endTime'] = datetime.datetime.now()
    action_record['actionStatus'] = 'failedActionStatus'
    action_record['error']  = {
        "@type": "thing",
        "name": "error",
        "description": error_message
    }
    return action_record



def clean(record):
    """Removes None values, empty lists and lists of one
    """
    if isinstance(record, list):

        if len(record) == 0:
            return None

        if len(record) == 1:
            return clean(record[0])

        new_record = []
        for i in record:
            new_i = clean(i)
            if new_i:
                new_record.append(new_i)

        return new_record

    elif isinstance(record, dict):
        new_record = {}
        for k, v in record.items():
            new_v = clean(v)
            if new_v:
                new_record[k] = new_v
        return new_record
    else:

        if isinstance(record, str):
            if record == 'null':
                return None
            if record == "":
                return None
            record = record.strip()

        return record


    '''
    return content

