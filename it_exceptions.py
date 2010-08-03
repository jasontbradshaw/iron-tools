
class ProcessAlreadyRunningError(Exception):
    """
    Indicates an attempt to start the same process twice.
    """

class ProcessOperationTimeoutError(Exception):
    """
    Indicates a process operation that timed out.
    """

class NoRecordedFileError(Exception):
    """
    Indicates an attempt to commit a time without a previous recording.
    """

class FileNotFoundError(Exception):
    """
    Indicates that a file could not be found.
    """

class InvalidOperationError(Exception):
    """
    Raised when a given operation is invalid in the context of current state.
    """
