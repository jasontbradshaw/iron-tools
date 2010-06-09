import time as t
import threading

def time():
    """
    Platform independent time based on an integer seconds.
    """
    return int(t.time())

class UnlockedAccessError(Exception):
    """
    Thrown when someone tries to acces the dictionary while it
    is unlocked.
    """
    
    pass

class ThreadedDataStore:
    def __init__(self):
        """
        Create an object that behaves as a standard dictionary,
        but is thread-safe.
        """
        
        # the dict we slap thread safety onto
        self.__dict = {}
        self.__default = None
        
        self.__lock = threading.Lock()
        self.__locked = False
    
    def __enter__(self):
        self.__locked = True
        self.__lock.acquire()
    
    def __exit__(self, typ = None, val = None, trace = None):
        self.__lock.release()
        self.__locked = False
    
    def __contains__(self, key):
        """
        Does the data store contain the given key?
        """

        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        return key in self.__dict
    
    def __getitem__(self, key):
        """
        Returns the item in the store at the time of access.
        """

        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        return self.__dict[key]
    
    def __len__(self):
        """
        Returns the number of items in the store.
        """
        
        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        return len(self.__data)

    def __setitem__(self, key, value):
        """
        Changes the item in the store to whatever is specified.
        """
        
        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        self.__dict[key] = value
    
    def __sizeof__(self):
        """
        Returns the number of items in the store.
        """
        
        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        return self.__dict.__sizeof__()
    
    def has_key(self, key):
        """
        Does the store contain the given key?
        """
        
        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        return self.__contains__(key)
    
    def items(self):
        """
        Returns a copy of all the (key, value) pairs at the time of
        access.
        """
        
        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        return self.__dict.items()
    
    def keys(self):
        """
        Returns all the keys in the store.
        """
        
        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        return self.__dict.keys()
    
    def values(self):
        """
        Returns all the values in the store.
        """
        
        if not self.__locked:
            raise UnlockedAccessError("Data store unlocked; access denied.")
        
        return self.__dict.values()
