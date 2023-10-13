import copy
import pytest

from labchronicle.core import LoggableObject


class SampleClass(LoggableObject):
    def sample_function(self, a, b, c=5):
        self.e = 0
        return a + b + c

    def another_function(self, x, y=10):
        return x * y


class TestLoggableObject:

    def test_setattr(self):
        log_obj = LoggableObject()

        # Test normal setattr operation
        log_obj.some_attr = "value"
        assert log_obj.some_attr == "value"

    def test_register_log_and_record_args_without_deepcopy(self):
        log_obj = LoggableObject()

        args = [1, 2]
        kwargs = {'c': 3}
        log_obj.register_log_and_record_args(SampleClass.sample_function, args, kwargs, record_details={},
                                             deepcopy=False)

        assert log_obj._register_log_and_record_args_map['SampleClass.sample_function'] == (args, kwargs, {})

    def test_register_log_and_record_args_with_deepcopy(self):
        log_obj = LoggableObject()

        args = [[1, 2], 3]
        original_args = copy.deepcopy(args)
        kwargs = {'c': [4, 5]}
        original_kwargs = copy.deepcopy(kwargs)

        log_obj.register_log_and_record_args(SampleClass.sample_function, args, kwargs, record_details={'g': 1})

        args[0].append(10)
        kwargs['c'].append(10)

        # Ensure original values are stored
        assert log_obj._register_log_and_record_args_map['SampleClass.sample_function'] != (args, kwargs, {'g': 1})
        assert log_obj._register_log_and_record_args_map['SampleClass.sample_function'] == (
            original_args, original_kwargs, {'g': 1})

        assert log_obj.retrieve_latest_record_entry_details(SampleClass.sample_function) == {'g': 1}

    def test_rebuild_args_dict(self):
        log_obj = LoggableObject()
        true_args = log_obj._rebuild_args_dict(SampleClass.sample_function, [1, 2], {'c': 3})

        assert true_args == {'a': 1, 'b': 2, 'c': 3}

    def test_rebuild_args_dict_with_missing_values(self):
        log_obj = LoggableObject()
        true_args = log_obj._rebuild_args_dict(SampleClass.sample_function, [1, 5], {})

        assert true_args == {'a': 1, 'b': 5, 'c': 5}  # since default c=5

    def test_retrieve_args(self):
        log_obj = LoggableObject()

        args = [1, 2]
        kwargs = {'c': 3}
        log_obj.register_log_and_record_args(SampleClass.sample_function, args, kwargs, record_details={})

        retrieved_args = log_obj.retrieve_args(SampleClass.sample_function)

        assert retrieved_args == {'a': 1, 'b': 2, 'c': 3}

    def test_retrieve_args_function_not_registered(self):
        log_obj = LoggableObject()

        with pytest.raises(ValueError,
                           match=r'Function SampleClass.another_function is not registered in LoggableObject.'):
            log_obj.retrieve_args(SampleClass.another_function)

    def test_retrieve_args_multiple_executions(self):
        log_obj = LoggableObject()

        args = [1, 2]
        kwargs = {'c': 3}
        log_obj.register_log_and_record_args(SampleClass.sample_function, args, kwargs, record_details={})
        log_obj.register_log_and_record_args(SampleClass.sample_function, [4, 5], {'c': 6}, record_details={})

        retrieved_args = log_obj.retrieve_args(SampleClass.sample_function)

        assert retrieved_args == {'a': 4, 'b': 5, 'c': 6}
