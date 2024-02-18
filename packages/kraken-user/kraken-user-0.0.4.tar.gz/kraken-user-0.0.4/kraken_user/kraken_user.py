
    
import copy
from kraken_user.helpers import json
from kraken_user.helpers import things
import os
import pkg_resources
import requests
import uuid
import datetime
import hashlib


"""
Notes:
To access files in data directory, use:
new_path = pkg_resources.resource_filename('kraken_user', old_path)

"""

records = {}



def delete(record):
    """
    """
    url = 'https://data.krknapi.com/kraken_login'

    headers = {"Content-Type": "application/json", "Authorization":"bob"}
    data = json.dumps(record)
    r = requests.delete(url, data=data, headers=headers)
    print(r.status_code)
    return


def post(record):
    """
    """


    records[record.get('membershipNumber', None)] = record
    
    url = 'https://data.krknapi.com/kraken_login'

    headers = {"Content-Type": "application/json", "Authorization":"bob"}
    data = json.dumps(record)
    r = requests.post(url, data=data, headers=headers)

    return


def add_user(record):
    """Register a new user
    """


    records[record.get('membershipNumber', None)] = record

    
    url = 'https://data.krknapi.com/kraken_login'

    headers = {"Content-Type": "application/json", "Authorization":"bob"}
    data = json.dumps(record)
    r = requests.post(url, data=data, headers=headers)

    return 


def get_user(program_name, record_id):
    """
    """


    if records.get(record_id, None):
        return records.get(record_id, None)
    

    url = 'https://data.krknapi.com/kraken_login'

    headers = {"Content-Type": "application/json", "Authorization":"bob"}

    params = {'@type': 'programMembership', 'programName': program_name, 'membershipNumber': record_id}

    r = requests.get(url, params=params, headers=headers)

    record = json.loads(r.content)

    records[record_id] = record
    
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

    post(record)
    return
        
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
    post(record)
    return record

def remove_role(record, role):

    for i in record.get('hasRole', []):
        if i.get('name', None) == role:
            i['validTo'] = datetime.datetime.now()
    post(record)
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
    post(record)
    return record


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
        "hasCredential": [
           
        ],
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


def add_login_event(record, remote_addr):
    """
    """
    event = {
        "@type": "action",
        "@id": str(uuid.uuid4()),
        "name": "login " + str(remote_addr),
        "timeStart": datetime.datetime.now(),
        "timeEnd": datetime.datetime.now(),
        "actionStatus": "completedActionStatus"
    }
    record['event'].append(event)
    return record