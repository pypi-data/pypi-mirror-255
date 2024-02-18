
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
    record = {
        "@type": "WebAPI",
        "@id": "75d41a03-7763-4c8f-a65b-52f80cdc7c77",
        "name": "kraken_user",
        "description": "description"
    }

    return record

def get_action_record(object_record, result_record=None):
    """
    """

    action_record = {
        '@type': 'action',
        '@id': str(uuid.uuid4()),
        'name': 'kraken_user',
        'object': object_record,
        'instrument': get_instrument_record(),
        'startTime': datetime.datetime.now(),
        'actionStatus': 'activeActionStatus'
    }

    if result_record:
        action_record['endTime'] = datetime.datetime.now()
        action_record['actionStatus'] = 'completedActionStatus'
        action_record['result'] = result_record

    return action_record



    