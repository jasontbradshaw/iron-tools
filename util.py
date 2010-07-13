import time
import threading

def get_time():
    """
    Platform independent time based on an integer seconds.
    """
    return int(time.time())

def block_until(condition_func, max_time):
    """
    Waits until the given function returns 'False' or the maximum time
    is exceeded, and returns whether the function returned 'True' or not.
    """
    
    return block_while(condition_func, max_time, invert=True)

def block_while(condition_func, max_time, invert=False):
    """
    Blocks while the given function returns 'True' (or 'False' if
    invert=True), then returns whether the condition was met before
    the maximum allotted time.
    """
    
    end_time = time.time() + max_time
    
    # flip the conditional function's test if specified
    if invert:
        term_test = lambda: not condition_func()
    else:
        term_test = condition_func
    
    # did we finish before the maximum time?
    success = True
    
    # wait until the condition function returns 'True' or exceeds its time
    while term_test():
        # we exceeded the maximum allotted time
        if time.time() > end_time:
            success = False
            break
        
        time.sleep(0.001)
    
    return success

def generate_file_name(basename, extension="dump"):
    """
    Generates a timestamped file name based on the base name and extension
    given.
    """
    
    timeformat = "%Y-%m-%d_%H:%M:%S"
    
    # create the file name in format: <timestamp><basename>.<extension>
    return time.strftime(timeformat) + basename + "." + extension

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
