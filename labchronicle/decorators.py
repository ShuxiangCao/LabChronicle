import decorator

from .logger import setup_logging
from .chronicle import Chronicle
from .core import LoggableObject

logger = setup_logging(__name__)


@decorator.decorator
def log_and_record(func, *args, **kwargs):
    """
    Decorator for the functions that want to be logged. The function must be a method of a LoggableObject.

    Parameters:
        func (function): The function to be logged.
        args (list): The arguments of the function.
        kwargs (dict): The keyword arguments of the function.

    Returns:
        Any: The return value of the function.

    Raises:
        RuntimeError: If the function is not a method of a LoggableObject.
    """
    if len(args) == 0:
        msg = f'Function {func.__qualname__} is not a class method.'
        logger.error(msg)
        raise RuntimeError(msg)

    self = args[0]

    if not isinstance(self, LoggableObject):
        msg = f'Function {func.__qualname__} is not a method of a LoggableObject.'
        logger.error(msg)
        raise RuntimeError(msg)

    chronicle = Chronicle()

    with chronicle.new_record() as record:
        if record is None:
            # There are no active record books. Simply execute the function.
            return func(*args, **kwargs)

        # Finalize the setup of the record.
        record.set_name(func.__qualname__)
        record.record_metadata()
        record.record_args(args[1:], kwargs)

        # Save the argument to the class as well.
        self.register_log_and_record_args(func, args[1:], kwargs)
        retval = func(*args, **kwargs)

        # Take a snapshot of the object after finish the function execution.
        record.record_object(self)

    return retval
