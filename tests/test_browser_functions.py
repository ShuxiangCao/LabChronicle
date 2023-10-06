from pytest import fixture

from labchronicle import register_browser_function
from labchronicle.core import LoggableObject


class SampleClass(LoggableObject):
    def sample_function(self, a, b, c=5):
        self.e = 0
        return a + b + c

    def another_function(self, x, y=10):
        return x * y

    @register_browser_function(a=1, b=2, c=3)
    def browser_function_1(self, x, y=10):
        return x * y

    @register_browser_function(a=3, b=4, c=5)
    def browser_function_2(self, x, y=10):
        return x * y + 1


@fixture
def loggable_object():
    return SampleClass()


def test_browser_functions(loggable_object):
    browser_functions = loggable_object.get_browser_functions()

    assert len(browser_functions) == 2

    assert browser_functions[0][0] == 'browser_function_1'
    assert browser_functions[0][1]._browser_function_kwargs == {'a': 1, 'b': 2, 'c': 3}

    assert browser_functions[1][0] == 'browser_function_2'
    assert browser_functions[1][1]._browser_function_kwargs == {'a': 3, 'b': 4, 'c': 5}

    assert browser_functions[0][1](1) == 10
    assert browser_functions[1][1](1) == 11
