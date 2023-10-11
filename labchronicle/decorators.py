import inspect

import decorator

from .logger import setup_logging
from .chronicle import Chronicle
from .core import LoggableObject

logger = setup_logging(__name__)


@decorator.decorator
def log_and_record(func, *args, **kwargs):
    """
    Decorator function for the functions that want to be logged. The function must be a method of a LoggableObject.
    Using this decorator will record the object and modified attributes within this function call
    after the function execution.

    Parameters:
        func (function): The function to be logged.
        args (list): The arguments of the function.
        kwargs (dict): The keyword arguments of the function.

    Returns:
        Any: The return value of the function.
    """
    return _log_and_record(func, args, kwargs)


@decorator.decorator
def log_event(func, *args, **kwargs):
    """
       Decorator function for the functions that want to be logged. The function must be a method of a LoggableObject.
       Using this decorator will only record return values and arguments of the function.

       Parameters:
           func (function): The function to be logged.
           args (list): The arguments of the function.
           kwargs (dict): The keyword arguments of the function.

       Returns:
           Any: The return value of the function.
       """
    return _log_and_record(func, args, kwargs, record_details=False)


def _log_and_record(func, args, kwargs, record_details=True):
    """
    Decorator function for the functions that want to be logged. The function must be a method of a LoggableObject.

    Parameters:
        func (function): The function to be logged.
        args (list): The arguments of the function.
        kwargs (dict): The keyword arguments of the function.
        record_details (bool): Optional. Whether to record the object and attributes after the function execution.
                                If false, only the arguments and return values are recorded.

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

    self.register_log_and_record_args(func, args[1:], kwargs)

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

        if record_details:
            self.set_record_entry(record)
        retval = func(*args, **kwargs)

        if record_details:
            self.set_record_entry()

        record.record_return_values(retval)

        # Take a snapshot of the object after finish the function execution.
        if record_details:
            record.record_object(self)

        self.logger.info(f'{record.uuid}:Function {func.__qualname__} recorded.')

    return retval


def register_browser_function(*args, **kwargs):
    """
    Decorator function for the functions that used to visualize data of the class.
     The function must be a method of a LoggableObject.

    Parameters:
        args (list): The arguments of the function.
        kwargs (dict): The keyword arguments of the function.

    Returns:
        Any: The return value of the function.
    """

    def inner_func(func):
        """
        Decorator function for the functions that used to visualize data of the class.
        The function must be a method of a LoggableObject.

        Parameters:
            func (function): The function to be registered.

        Returns:
            Any: The same function.
        """

        func._browser_function = True
        func._browser_function_args = args
        func._browser_function_kwargs = kwargs

        return func

    return inner_func
