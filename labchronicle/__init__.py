from .logger import setup_logging
from .chronicle import Chronicle, load_object, load_attributes
from .core import LoggableObject
from .decorators import log_and_record, log_event, register_browser_function

browser_function = register_browser_function  # Alias for backwards compatibility

log = None  # Chronical log instance, None if not running
logger = setup_logging(__name__)
