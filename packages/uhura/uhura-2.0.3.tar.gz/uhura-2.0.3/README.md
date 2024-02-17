# Uhura  
  
A framework for tackling legacy data engineering code.  
  
Wrap inputs and outputs for your system and take advantage of asyncio + automated testing.  
  
Uhura makes it easy to run pipelines in a specific "mode". Modes are implemented using context managers and are stored in the `modes` module. Right now Uhura supports two main use cases:  
1. A testing mode used to run a pipeline and compare its output against pre-generated fixtures. This is executed through the `fixture_builder_mode` and the `task_test_mode` contexts.  
2. A mode used for testing whether functions respect specific properties. This is executed through the `test_transformers` context.  
  
More details on how to run the two modes can be found in the Examples section below  
  
## Examples  
  
### 1. Pipeline testing mode  
Imagine you have some legacy ETL code:  
```python
import pandas as pd  
  
  
def load_data() -> pd.DataFrame: ... # IO code here  
  
  
def load_ids_of_interest() -> set[int]: ... # More IO code  
  
  
async def write_filtered_data(df: pd.DataFrame): ...  
  
  
async def main():  
	data = load_data()  
	ids = load_ids_of_interest()  
	await write_filtered_data(data[data['id'].isin(ids)])  
  
```
These functions might be reading from, and writing to, live cloud resources. They may also be loading  
large amounts of data, all of which makes it tricky/ unsafe to run this code locally.  
  
If something goes wrong we can use logging to try and understand what's going on in the cloud. But  
print statement debugging is no substitute for a proper local debugger. If we had decently separated  
IO and business logic we might be able to use local unit tests, but the existing code might not be  
set up for this, and refactoring without tests in the first place is quite risky.  
  
To solve this problem, uhura allows you to wrap arbritary IO code, and substitute it when testing.  
It also contains tools to speed up the process of building local end-to-end tests.  
  
So what does this wrapping process look like?  
  
First we decorate our functions which provide inputs or outputs:  
  
```python
import pandas as pd  
from uhura.functional import uhura_reader, uhura_writer  
  
  
@uhura_reader  
def load_data() -> pd.DataFrame: ... # IO code here  
  
  
@uhura_reader  
def load_ids_of_interest() -> set[int]: ... # More IO code  
  
  
@uhura_writer  
async def write_filtered_data(df: pd.DataFrame): ...  
```

  
Uhura supports both async and sync input and output functions. As well as generators and async iterators.  
  
But what do we gain from doing this? The answer lies in the uhura 'modes'.  
  
Modes let us change the behaviour of our uhura classes to gain certain benefits. A good  
starting example is the 'fixture_builder_mode' which lets us store a local copy of each  
input and output, which can speed up testing when our underlying code is reaching out the  
internet / running queries, and also means that we don't actually write anything out to the  
real systems we interact with.  
  
For example:  
```python
from uhura.modes import fixture_builder_mode  
from time import sleep  
  
  
@uhura_reader  
def expensive_input():  
	sleep(10) # Expensive IO operation  
	return 1  
  
  
with fixture_builder_mode():  
	assert expensive_input() == 1 # This takes a while...  
	assert expensive_input() == 1 # This executes instantly!  
  
  
# Now we can start testing. First we need to stage our data.  
  
from uhura.modes import fixture_builder_mode  
from asyncio import run  
  
  
with fixture_builder_mode():  
	run(main())  
```

By running our code in this context manager, we replace each reader with a 'pull through proxy' which  
will call the underlying code and save the result to a location in the local filesystem. It will only  
do this is there isn't already some data there, which lets us quickly rebuild parts of our fixtures  
without having to rebuild everything.  
  
Now it's time to test things.  
```python
from uhura.modes import task_test_mode  
  
  
with task_test_mode():  
	main()  
```
In this mode, all inputs will be replaced with the staged inputs saved by the fixture_builder_mode,  
and all outputs will be automatically compared with the staged outputs. If the outputs differ, Uhura  
will raise an exception highlighting exactly what's changed.  
  
#### Class based API  
  
Decorating functions will address common requirements, but uhura also supports having reader and writer classes.  
These are often useful for when a resource is both read and written within a codebase.  
```python
from uhura.base import Readable, Writable  
from uhura.modes import fixture_builder_mode  
  
class ItemClient(Readable[int], Writable[int]):  
	def read(self):  
		return 1  
  
def write(self, obj):  
	print(f"Writing {obj}")  
	pass  
  
with fixture_builder_mode():  
	client = ItemClient()  
	client.write(client.read() + 1) # Caches locally  
```
  
The class based API also has some additional features beyond the basic decorators, such as overriding the cache  
key (see below).  
  
  
  
### Gotchas  
  
#### Caching Mechanism  
  
Note, the readers and writers *do not* take the arguments to their constructors into account, there will be one  
fixture for each reader and writer by default.  
```python
_fake_database = {"id1": 27, "id2": 34}  
  
class DatabaseReader(Readable[int]):  
	def __init__(self, id_: str):  
		self._id = id_  
  
	def read(self):  
		return _fake_database[self._id]  
  
with fixture_builder_mode():  
	assert DatabaseReader("id1").read() == 27  
	assert DatabaseReader("id2").read() == 34 # This will fail it returns just 27 again  
  
```
  
If the required arguments are known at definition time you can create multiple classes or functions for different  
resources. Alternately this behaviour can be overridden by implementing the 'cache_key' hook method on a  
corresponding class.  
  
```python
_fake_database = {"id1": 27, "id2": 34}  
  
class DatabaseReader(Readable[int]):  
	def __init__(self, id_: str):  
		self._id = id_  
  
def read(self):  
	return _fake_database[self._id]  
  
def cache_key(self):  
	return f"DatabaseReader/{self._id}"  
  
with fixture_builder_mode():  
	assert DatabaseReader("id1").read() == 27  
	assert DatabaseReader("id2").read() == 34 # Success!  
```

#### Inheritance  
  
Uhura will only apply changes to classes which directly subclass Uhura types, not classes subclassed from those initial  
classes.  
  
Subclasses of those classes will only immediately work with Uhura if they delegate all the relevant methods to their  
parent (e.g. read, write, cache_key).  
  
You can safely inherit from Uhura base types at multiple points in your hierarchy if needed.  
  
### Custom Comparisons  
  
In task_test_mode, the default comparison is normally fairly good. But in some situations it won't  
be sufficient. This includes when outputs include things like 'last_processed' timestamps. The  
following example gives an instance of this:  
```python
from datetime import datetime  
  
  
class OutputWriter(Writable[dict]):  
	def write(self, obj: dict):  
		...  
```
  
def write_out_result(result: int):  
return OutputWriter().write({"result": result, "time_processed": datetime.now()})  
  
  
What we can do in this case is add a pre-processor to the comparison for the relevant class. The  
syntax for that is as follows.  
```python
from uhura.modes import default_comparator  
  
  
def _drop_time_processed(output: dict):  
	del output["time_processed"]  
	return output  
  
  
default_comparator["OutputWriter"].add_preprocessor(_drop_time_processed)  
  
with task_test_mode():  
	...  
```
  
### Editing Fixtures  
  
Fixtures are stored as pickle files, by default under:  
  
known_good_path = "tests/fixtures/output_known_good"  
input_path = "tests/fixtures/input"  
  
The known good path storing written outputs.  
  
There is one file for each client, named '{client_name}.pkl'.  
  
If you have specified a custom cache_key, this will form the file name of the fixture instead.  
  
  
These can be edited manually (for instance if you want to downsample data). Relevant outputs  
can then be deleted and regenerated using the fixture_builder_mode.  
  
### Custom Serde  
  
By default uhura stores all fixtures as pickle files, in some settings other formats may be  
preferable. This can be specified by overriding the 'get_serde' method on readers and writers.  
  
```python
import pandas as pd  
from uhura.serde import ParquetSerde  
  
  
class ParquetReader(Readable[pd.DataFrame]):  
    def read(self):  
        return _load_from_external()  
  
    def get_serde(self):  
        return ParquetSerde(read_kwargs={"engine": "fastparquet"})  
```
  
Additional serde classes can be implemented by implementing the 'uhura.serde.Serde' interface.  
  
  
### 2. Properties testing mode  
  
Let's say that you want to know whether a function operating on a dataframe will return a different output if the dataframe is sorted differently or whether a function will modify a specific column in the dataframe. Rather than reading the functions code you can write a property to check for these behaviors and then let Uhura figure out whether these functions behave as expected.  
  
Properties are stored in the `uhura/properties/testable_properties` module. As an example let's look at the property checking whether a function output is affected by the order of records in the dataframe passed as an argument  
```python  
import pandas as pd  
from typing import Optional  
from uhura.properties.homomorphic_hash import homomorphic_hash  
from uhura.properties.testable_properties import SENTINEL  
  
def order_invariant(tested, arg: pd.DataFrame, result: Optional[pd.DataFrame] = None):  
	"""Check whether `tested` output is affected by the order of the rows in `arg`  
	  
	Args:  
		tested (Callable): the function for which we are testing the property  
		arg (pd.DataFrame): the dataframe over which we want to run the function being tested  
		result (pd.DataFrame): the result of `tested(arg)` this may already be passed as an argument in case it is  
		available, and we don't need to run again `tested(arg)` to check the property. So, that we can avoid  
		running `tested` unnecessarily.  
	Returns:  
		pd.DataFrame: The output of running the tested function on the main dataframe ie `tested(arg)`  
		bool: It tells if the property is respected  
	"""  
	shuffled_result = homomorphic_hash(tested(arg.sample(frac=1)).sort_index())  
	result = tested(arg) if result is SENTINEL else result  
	return result, homomorphic_hash(result.sort_index()) == shuffled_result  
```  
  
All properties should have the same signature, as per docstring. Optionally a property can also return a third object, a string containing some notes regarding the property.  
  
In order to run a property on a specific function you need to decorate the function with the transformer method.  
```python  
import pandas as pd  
from uhura.properties import transformer  
  
  
@transformer  
def function_that_respect_property(df: pd.DataFrame):  
	...  
	return df  
  
@transformer(evaluated_arg_name="df_b")  
def function_that_respect_property(df_a: pd.DataFrame, df_b: pd.DataFrame):  
	...  
	return df_a  
```  
  
in case the function takes multiple arguments you can specify which one should be used with the function when testing the property. In order to do so it's enough to pass its name to `evaluated_arg_name` in the transformer.  
  
Most of the time the property is tested on the function by comparing the input and the main output of the function. So, the function has to have a single output for the workflow to work as expected. That output is what is going to be compared against the function input.  
  
Once you have decorated the functions you care about property-checking you need to specify what properties you want to test while running the pipeline. You can easily do so through the `PropertyTester` object. Let's say I want to test whether a function output is going to be affected by how its input dataframe is sorted and also whether a few specific columns are being modified (`col_a` and `col_d`)  
```python  
from uhura.properties import PropertyTester, order_invariant, get_columns_not_modified_property  
  
tester = PropertyTester.create_for_properties(  
	[order_invariant, get_columns_not_modified_property(["col_a", "col_d"])]  
)  
```  
  
Once we defined the property functions, we decorated the functions we want to test the properties on, and we created a property_tester object we can then use this to run the property testing mode.  
```python  
from uhura.modes import test_transformers  
from uhura.properties import PropertyTester, order_invariant, get_columns_not_modified_property  
  
def main():  
	# our main pipeline including the functions we decorated with `@transformer`  
	...  
	pass  
  
tester = PropertyTester.create_for_properties(  
	[order_invariant, get_columns_not_modified_property(["col_a", "col_d"])]  
)  
  
with test_transformers(tester):  
	main()  
```  
  
By default, the logs are used to show whether the properties are respected on the functions. However, the output can be redirected somewhere else if preferred. As an example you can find below how the properties info appears in the logs.  
```txt  
2023-05-02 10:48:58,580 [INFO] uhura: [find_maiden_voyages]: has property order_invariant  
2023-05-02 10:48:58,610 [INFO] uhura: [find_maiden_voyages]: has property get_columns_not_modified_property.<locals>.columns_not_modified -  
2023-05-02 10:48:58,749 [INFO] uhura: [prepare_vessel_status]: lacks property order_invariant  
2023-05-02 10:48:59,810 [INFO] uhura: [insert_voyage_id]: lacks property order_invariant  
2023-05-02 10:49:01,423 [INFO] uhura: [prepare_model_output]: lacks property order_invariant  
```  
  
#### Caveats  
When importing a library in another codebase by default its logger will be disabled, so if you want the uhura logs to be made available you will need to explicitly enable it, as per below:  
```python  
import logging  
  
from uhura.properties import UHURA_PROPERTIES_LOGGER_NAME  
  
logging.getLogger(UHURA_PROPERTIES_LOGGER_NAME).disabled = False  
```