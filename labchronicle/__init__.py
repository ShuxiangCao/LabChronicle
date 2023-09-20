from .logger import setup_logging

log = None  # Chronical log instance, None if not running
logger = setup_logging(__name__)
