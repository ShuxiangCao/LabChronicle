# LabChronicle

[![Test](https://github.com/ShuxiangCao/LabChronicle/actions/workflows/test.yaml/badge.svg)](https://github.com/ShuxiangCao/LabChronicle/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/ShuxiangCao/LabChronicle/graph/badge.svg?token=EDDTTE9Q9P)](https://codecov.io/gh/ShuxiangCao/LabChronicle)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LabChronicle is a Python package to track the execution of Python classes, particularly for physical experiments, and
stores their values. The way LabChronicle works is by monitoring the decorated functions, detecting any access to the
class attribute, and marking them modified. The modified attributes are then stored in a database, after the function
call finishes, and can be retrieved afterwards. Optionally a snapshot of the entire object can be also captured at
the end of the function call, to allow for a more detailed analysis of the object state.

## Concept

+ *Loggable object*: Loggable object are python class instance, it contains the full configurations and parameters,
  analysis and result and visualization for an experiment. The actual function must be a class method of a Loggable
  object.
+ *Record entry*: When a loggable function is called, one record entry is created. The record entry contains the
  function
  name, arguments, return value, and the modified attributes. It optionally also contains a snapshot of the loggable
  object.
+ *Record book*: Record book is a tree structure database that contains multiple record entries. It usually represents a
  full experiment run, where multiple loggable function is called.

## Installation

LabChronicle can be installed using pip from the source code:

```bash
pip install ./labchronicle
```

## Usage

### Data storage

LabChronicle supports multiple database handlers. The default backend is using  `hdf5` files to store the data. Each
experiment is stored in a separate file, and the file name is the experiment name. Two environment variables are used
to specify the database location and handler.

+ `LAB_CHRONICLE_LOG_DIR`: The directory where the database is stored. The default value is `./log`.
+ `LAB_CHRONICLE_HANDLER`: The database handler. The default value is `hdf5`.

Note that the log dir is the directory not the file path to the experiment file. The experiment file is stored in the
format of `log_dir / jupyter_user / year_month / day / day_time` where `jupyter_user` is the user name of the
jupyterhub,
if not using jupyterhub, the system username will be used.

### Tracking

LabChronicle can be used by importing the `labchronicle` module. The classes that need to be tracked should inherent the
`labchronicle.LoggableObject` class. The `labchronicle` module provides a decorator `@labchronicle.log_and_record` that
can be used to track the function calls, and take a snapshot of the module. The decorator can be used as follows:

For each experiment, the experiment environment will be logged as well, depending on the handler.

The information being tracked by LabChronicle are:

+ The function call, including the arguments and return value
+ The class attributes that are modified during the function call

Here is an example of how to use LabChronicle:

```python
import labchronicle


class MyClass(labchronicle.LoggableObject):
    def __init__(self):
        super().__init__()
        self.a = 1
        self.b = 2

    @labchronicle.log_and_record
    def my_function(self, x):
        self.a = x
        self.b = x + 1
        return self.a + self.b


ch = labchronicle.Chronicle()  # Access the chronicle manager
ch.start_log('my_experiment_name')  # Start a new experiment log
# Relax and enjoy the experiment
my_object = MyClass()
my_object.my_function(3)
ch.end_log()

```

The `my_function` function is now tracked by LabChronicle. The function can be called as usual, and the return value
will be the same as before. However, the function call is now logged, and the values of `a` and `b` are stored in the
database. The database can be accessed using the `labchronicle` module.

### Data retrieval

The simplest way to access the saved log file is by using the following short cut functions:

```python
#just need to specify either record_id or record_entry_path
exp_obj = labchronicle.load_object(record_book_path, record_id, record_entry_path)  
exp_attributes = load_attributes(record_book_path, record_id, record_entry_path)
```

For more detailed data retrieval, the `labchronicle` module provides a `Chronicle` class that
can be used to access the database. The `Chronicle` class can be initialized with the experiment name.
See example here:

```python
ch = labchronicle.Chronicle()
record_book = ch.open_record_book('path_to_experiment_file')  # Usually specified 
root_entry = record_book.get_root_entry()
children = root_entry.children  # These are the record entries

# Now lets get the record entry
record = children[0]
record.name == 'my_function'  # True
record.get_recorded_attribute_names() == ('x',)  # True
record.load_attribute('x') == 3  # True
obj = record.get_object()  # Load the snapshot
obj.a == 3  # True
record.load_return_value() == 7  # True
```

Note that each log entry is associated with an id, is expected to be printed after the experimental call when needed.
The record entry can be directly loaded by the id.

```python
record = record_book.get_record_entry_by_id("The uuid of the record")
```

## Testing

The test can be run using `pytest`:

```bash
pytest
```

## License

LabChronicle is licensed under the MIT license. See the LICENSE file for details.

## Acknowledgement

LabChronicle is developed by Shuxiang Cao @ [Leeklab](https://leeklab.org), University of Oxford. For any questions,
please contact [Shuxiang Cao](mailto:shuxiang.cao@physics.ox.ac.uk).
