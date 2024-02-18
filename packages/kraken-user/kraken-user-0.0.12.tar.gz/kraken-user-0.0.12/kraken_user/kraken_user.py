
    
import copy
from kraken_user.helpers import json
from kraken_user.helpers import things
import os
import pkg_resources
import requests
import uuid
import datetime
import hashlib
import copy

"""
Notes:
To access files in data directory, use:
new_path = pkg_resources.resource_filename('kraken_user', old_path)

"""

records = {}


"""
Cache
"""


def get_from_cache(membershipNumber):
    """
    """

    if not membershipNumber:
        return None
    
    if records.get(membershipNumber, None):
        return records.get(membershipNumber, None)

    return None


def post_to_cache(record):
    """
    """

    if not record:
        return None
    
    if isinstance(record, list):
        for i in record:
            post_to_cache(i)
        return
        
    records[record.get('membershipNumber', None)] = record

    return

def delete_from_cache(membershipNumber):
    """
    """
    if not membershipNumber:
        return None
        
    records.pop(membershipNumber, None)
    return 
    



"""
I/O
"""

def delete(record):
    """
    """
    url = 'https://data.krknapi.com/kraken_login'

    headers = {"Content-Type": "application/json", "Authorization":"bob"}
    data = json.dumps(record)
    r = requests.delete(url, data=data, headers=headers)
   
    delete_from_cache(record.get('membershipNumber', None))
    return


def post(record):
    """
    """
    
    post_to_cache(record)
    
    url = 'https://data.krknapi.com/kraken_login'

    headers = {"Content-Type": "application/json", "Authorization":"bob"}
    data = json.dumps(record)
    r = requests.post(url, data=data, headers=headers)

    return


def create_user(record):
    """Register a new user
    """


    program = record.get('programName', None)
    membershipNumber = record.get('membershipNumber', None)

    if not program:
        return False

    if not membershipNumber:
        return False

    # Check if record exists
    db_record = get_user(program, membershipNumber)
    if db_record:
        # Handle situation where user already exists
        return False

    original_record = copy.deepcopy(record)
    #
    record = add_event(record, 'create user', original_record)
    
    # Set active
    record = set_active_status(record)
    
    # Create record
    post(record)
    
    return record


def get_user(program_name, membershipNumber):
    """
    """

    if not program_name or not membershipNumber:
        return None
    
    if get_from_cache(membershipNumber):
        return get_from_cache(membershipNumber)
    

    url = 'https://data.krknapi.com/kraken_login'

    headers = {"Content-Type": "application/json", "Authorization":"bob"}

    params = {'@type': 'programMembership', 'programName': program_name, 'membershipNumber': membershipNumber}

    r = requests.get(url, params=params, headers=headers)


    if r.status_code != 200:
        return None
    
    record = json.loads(r.content)

    if isinstance(record, list) and len(record) > 0:
        return record[0]
    if isinstance(record, list) and len(record) == 0:
        return None

    post_to_cache(record)
    
    return record


def get_users(program_name):
    """
    """


    url = 'https://data.krknapi.com/kraken_login'

    headers = {"Content-Type": "application/json", "Authorization":"bob"}

    params = {'@type': 'programMembership', 'programName': program_name,}

    r = requests.get(url, params=params, headers=headers)

    records = json.loads(r.content)

    return records


"""
Credentials
"""


def add_credential(record, password_value, salt_value):
    """
    """

    hash_password = get_hash_password(password_value, salt_value)

    if not record.get('hasCredential', None):
        record['hasCredential'] = []

    # Cancel existing credentials
    for i in record.get('hasCredential', []):
        validTo =  i.get('validTo', None)
        if not validTo or validTo > datetime.datetime.now():
            i['validTo'] = datetime.datetime.now()

    # Create new credential
    credential = {
        "@type": "credential",
        "@id": str(uuid.uuid4()),
        "validFrom": datetime.datetime.now(),
        "validTo": None,
        "proof": {
              "type": "DataIntegrityProof",
              "verificationMethod": "hash",
              "proofPurpose": "assertionMethod",
              "proofValue": hash_password
        }
    }
    record['hasCredential'].append(credential)
    record = add_event(record, 'add credential', credential)
    return record


def authenticate_user(record, password_value, salt_value):
    """
    """

    hash_password = get_hash_password(password_value, salt_value)

    for i in record.get('hasCredential', []):
        proof = i.get('proof', {})
        c1 = i.get('validFrom', None) < datetime.datetime.now()
        c2a = i.get('validTo', None) == None
        c2b = i.get('validTo', None) and i.get('validTo', None) > datetime.datetime.now()
        c3 = proof.get('proofValue', None) == hash_password

        if c1 and (c2a or c2b) and c3:
            return True

    return False


def cancel_passwords(record):
    """Cancels all current passwords
    """

    for i in record.get('hasCredential', []):
        validTo =  i.get('validTo', None)
        if not validTo or validTo > datetime.datetime.now():
            i['validTo'] = datetime.datetime.now()

    record = add_event(record, 'remove credentials')
    
    return


"""
Roles
"""
def add_role(record, role):
    """
    """

    if not record.get('hasRole', None):
        record['hasRole'] = []

    # Create new credential
    role = {
        "@type": "role",
        "@id": str(uuid.uuid4()),
        "validFrom": datetime.datetime.now(),
        "validTo": None,
        "name": role
    }
    record['hasRole'].append(role)

    record = add_event(record, 'add role', role)

    return record

def remove_role(record, role):

    for i in record.get('hasRole', []):
        if i.get('name', None) == role:
            i['validTo'] = datetime.datetime.now()
            record = add_event(record, 'remove role', i)
    
    return record

def get_active_roles(record):

    active_roles = []
    for i in record.get('hasRole', []):
        c1 = i.get('validFrom', None) < datetime.datetime.now()
        c2a = i.get('validTo', None) == None
        c2b = i.get('validTo', None) and i.get('validTo', None) > datetime.datetime.now()

        if c1 and (c2a or c2b) :
            active_roles.append(i.get('name', None))
    return active_roles

def get_active_status(record):
    """Returns True if 'member' role is active
    """
    if 'member' in get_active_roles(record):
        return True
    return False

def set_active_status(record):
    """Add member role
    """
    if not get_active_status(record):
        record = add_role(record, 'member')
        record = add_event(record, 'set active')

    return record


def set_inactive_status(record):
    """Remove member role
    """

    record = remove_role(record, 'member')
    record = add_event(record, 'set inactive')
    return record

"""
Base record
"""


def get_base_record():
    """
    """

    record = {
        "@type": "programMembership",
        "@id": str(uuid.uuid4()),
        "hostingOrganization": None,
        "member": {
            "@type": "person",
            "@id": None,
            "email": None
        },
        "programName": None,
        "membershipNumber": None,
        "hasCredential": [],
        "hasRole": [],
        "event": []
    }
    
    return record

def get_hash_password(password_value, salt_value):
    """
    """
    m = hashlib.sha256()
    m.update(bytes(password_value,'UTF-8'))
    m.update(bytes(salt_value,'UTF-8'))
    m.digest()

    result = m.hexdigest()

    return result

"""
Events
"""


def add_event(record, name, object=None, status='completedActionStatus'):
    """
    """

    # Add event
    timeEnd = datetime.datetime.now() if status in['completedActionStatus', 'failedActionStatus'] else None
    creation_event = {
        "@type": "action",
        "@id": str(uuid.uuid4()),
        "name": name,
        "timeStart": datetime.datetime.now(),
        "timeEnd": timeEnd,
        "object": object,
        "actionStatus": status
    }

    if not record.get('event', None):
        record['event'] = []

    if not isinstance(record.get('event', None), list):
        record['event'] = [record.get('event', None)]
        
    record['event'].append(creation_event)

    return record




def add_login_event(record, remote_addr=None):
    """
    """

    # Add login event
    record = add_event(record, 'login')

    # Add session event
    record = add_event(record, 'session', None, 'activeActionStatus')

    return record

def add_failed_login_event(record, remote_addr=None):
    """
    """
    record = add_event(record, 'login', None, 'failedActionStatus')

    return record


def add_logout_event(record, remote_addr=None):
    """
    """
    # Add login event
    record = add_event(record, 'logout')

    # Update session event
    for i in record.get('event', []):
        status = i.get('actionStatus', None)
        name = i.get('name', None)
        timeEnd = i.get('timeEnd', None)
        if name == 'session' and status == 'activeActionStatus':
            i['timeEnd'] = datetime.datetime.now()
            i['actionStatus'] = 'completedActionStatus'
    return record

def is_logged_in(record):
    """
    """
    for i in record.get('event', []):
        status = i.get('actionStatus', None)
        name = i.get('name', None)
        timeEnd = i.get('timeEnd', None)
        if name=='session' and status == 'activeActionStatus':
            return True

    return False
    

    