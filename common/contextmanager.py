"""
common > contextmanager

Contains the DeviceContextManager class, used to manage the state of the script,
allowing for soft resets of the script when required.

Author: Miguel Guthridge [hdsq@outlook.com.au]
"""

from typing import NoReturn, Optional, Callable
from pprint import pprint

from .settings import Settings

class DeviceContextManager:
    """Defines the context for the entire script, which allows the modular
    components of script to be dynamically refreshed and reloaded, as well as
    be reset to the default start-up state if required.
    
    It is gettable from any location by using the getContext() method
    """
    
    def __init__(self) -> None:
        """Initialise the context manager, including reloading any required
        modules
        """
        
        self.settings = Settings()
    
    def initialise(self) -> None:
        """Initialise the controller associated with this context manager.
        """

    def processEvent(self, event) -> None:
        """Process a MIDI event

        ### Args:
        * `event` (`event`): event to process
        """
    
    def tick(self) -> None:
        """Called frequently to allow any required updates to the controller
        """

class ContextResetException(Exception):
    """Raised when the context is reset, so as to prevent any other operations
    using the old context from succeeding
    """

def catchContextResetException(func: Callable)-> Callable:
    """A decorator for catching ContextResetExceptions so that the program
    continues normally

    ### Args:
    * `func` (`Callable`): function to decorate

    ### Returns:
    * `Callable`: decorated function
    """
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ContextResetException:
            pass
    return wrapper

# The context manager's instance
# This should be the only non-constant global variable in the entire program,
# except for the log
_context: Optional[DeviceContextManager] = None

def getContext() -> DeviceContextManager:
    """Returns a reference to the device context

    ### Raises:
    * `Exception`: when the context is `None`, indicating that it wasn't
      initialised

    ### Returns:
    * `DeviceContextManager`: context
    """
    if _context is None:
        raise Exception("Context isn't initialised")
    
    return _context

def resetContext(reason:str="") -> NoReturn:
    """Resets the context of the script to the default, before raising a
    ContextResetException to halt the current event

    ### Args:
    * `reason` (`str`, optional): reason for resetting. Defaults to "".

    ### Raises:
    * `ContextResetException`: halt the event's processing
    """
    global _context
    logger.log(
        "bootstrap.context.reset",
        f"Device context reset with reason: {reason}",
        logger.verbosity.WARNING)
    _context = DeviceContextManager()
    raise ContextResetException(reason)

def _initContext() -> None:
    global _context
    _context = DeviceContextManager()

_initContext()

import logger