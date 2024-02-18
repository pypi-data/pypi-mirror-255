import uuid
from collections import namedtuple

class SingletonMeta(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Utils():
    
    @classmethod
    def get_guid(self):
        Guid = uuid.uuid4().hex
        return Guid
    
    @classmethod
    def custom_entity_decoder(self, entityDictionary):
        return namedtuple('X', entityDictionary.keys())(*entityDictionary.values())
