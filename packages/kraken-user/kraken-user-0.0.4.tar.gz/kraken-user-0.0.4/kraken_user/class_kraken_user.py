
    
import copy
import uuid
import os
import pkg_resources
from kraken_user.helpers import json
from kraken_user import kraken_user as m

"""
Notes:
To access files in data directory, use:
new_path = pkg_resources.resource_filename('kraken_user', old_path)

"""





class User:
    """
    The Vehicle object contains a lot of vehicles

    Args:
        arg1 (str): The arg is used for...
        arg2 (str): The arg is used for...
        arg3 (str): The arg is used for...

    Attributes:
        _objects: List of all objects initialized with this class
        record (dict): This is where we store attributes
        json (str): Record in json format
        
    """

    _objects = []    # Initialize array to store all objects instances

    def __init__(self):
        
        User._objects.append(self)    # Add itself to list of objects instances

        self._id = str(uuid.uuid4())
        self._record = m.get_base_record()
        self._index = 0
        self._salt = '36b8e053-2c43-4107-b51f-e2ebd05f3838'

    def __str__(self):
        """
        """
        return str(self._record)

    
    def __repr__(self):
        """
        """
        return str(self._record)

    def __iter__(self):
        """ Allows the object to be used in a for loop as a array of only itself
        """
        self._index=0
        return self

    def __next__(self):
        if self._index == 0:
            self._index = 1
            return self
        else:
            self._index = 0
            raise StopIteration


    
    def __eq__(self, other):
        """
        """
        if type(self) != type(other):
            return False
            
        if self._record == other._record:
            return True
        return False

    def __gt__(self, other):
        """
        """
        return True


    
        
    def set(self, property, value):
        """
        """
        self._record[property] = value
        return True

    
    def get(self, property):
        """
        """
        return self._record.get(property, None)

    
    def load(self, value):
        """
        """
        self._record = value
        return True


    def dump(self): 
        """
        """
        return copy.deepcopy(self._record)
        

    def set_json(self, value):
        """
        """
        record = json.loads(value)
        self.load(record)
        return True

    def get_json(self):
        """
        """
        return json.dumps(self.dump())

    @property
    def record(self):
        return self.dump()

    @record.setter
    def record(self, value):
        return self.load(value)
    
    @property
    def json(self):
        return self.get_json()

    @json.setter
    def json(self, value):
        return self.set_json(value)
        




    @property
    def is_authenticated(self):
        """
        """

        return True if self.status == 'authenticated' else False


    @property
    def is_active(self):
        """
        """

        return True if self.status == 'authenticated' else False


    @property
    def is_anonymous(self):
        """
        """

        return False if self.id else True


    def get_id(self):
        """
        """
        return self._record.get('@id', None)

    def set_email(self, value):
        """
        """
        self._record['membershipNumber'] = value
        self._record['member']['email'] = value
    

    @property
    def email(self):
        return self._record.get('member', {}).get('email', None)

    @email.setter
    def email(self, value):
        self.set_email(value)

    
    def set_programName(self, value):
        """
        """
        self._record['programName'] = value

    @property
    def program(self):
        return self._record.get('programName', None)

    @program.setter
    def program(self, value):
        self.set_programName(value)

    

    def authenticate(self, password):
        """
        """
        return m.authenticate_user(self.record, password, self._salt)
    
    def get(self, userid):
        """
        """
        self._record = m.get_user(self.program, userid)
        return   
        
    def add_credential(self, password_vlaue):
        """
        """
        self.record = m.add_credential(self.record, password_value, self._salt)
        
    def set_password(self, password_value):
        """
        """
        self.record = m.add_credential(self.record, password_value, self._salt)

    def delete(self):
        """
        """
        m.delete(self.record)
        self._record = m.get_base_record()


    def get_hash(self, password_value):
        """
        """
        return m.get_hash_password(password_value, self._salt)



    def add_role(self, role):
        self._record = m.add_role(self.record, role)

    def remove_role(self, role):
        self._record = m.remove_role(self.record, role)

    def get_active_roles(self):
        return m.get_active_roles(self.record)

    def add_login_event(self, remote_addr):
        self._record = m.add_login_event(self.record, remote_addr)