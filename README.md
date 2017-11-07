# pytest-fauxfactory

[![Downloads](https://pypip.in/download/pytest-fauxfactory/badge.svg?style=flat)](https://pypi.python.org/pypi/pytest-fauxfactory/)
[![Latest version](https://pypip.in/version/pytest-fauxfactory/badge.svg?style=flat)](https://pypi.python.org/pypi/pytest-fauxfactory/)
[![Supported Python versions](https://pypip.in/py_versions/pytest-fauxfactory/badge.svg?style=flat)](https://pypi.python.org/pypi/pytest-fauxfactory/)
[![License](https://pypip.in/license/pytest-fauxfactory/badge.svg?style=flat)](https://pypi.python.org/pypi/pytest-fauxfactory/)
[![Format](https://pypip.in/format/pytest-fauxfactory/badge.svg?style=flat)](https://pypi.python.org/pypi/pytest-fauxfactory/)


Now you pass random data to your tests using this **Pytest** plugin for [FauxFactory](https://github.com/omaciel/fauxfactory).

The easiest way to use it is to decorate your test with the `gen_string` mark and write a test that expects a `value` argument:

```python
@pytest.mark.gen_string()
def test_generate_alpha_strings(value):
    assert value
```

By default a single random string will be generated for your test.

```shell
test_generate_alpha_strings[:<;--{#+,&] PASSED
```

Suppose you want to generate **4** random strings (identified as **value**) for a test:

```python
@pytest.mark.gen_string(4, 'alpha')
def test_generate_alpha_strings(value):
    assert value.isalpha()
```

You will then have 4 tests, each with different values:

```shell
test_generate_alpha_strings[EiOKPHSXNYfv] PASSED
test_generate_alpha_strings[BBATlPxwmHaP] PASSED
test_generate_alpha_strings[kXIGIIXOyZyv] PASSED
test_generate_alpha_strings[eqHxEFneSKNC] PASSED
```

Now, suppose you also want to make sure that all strings have exactly 43 characters:

```python
@pytest.mark.gen_string(4, 'alpha', length=43)
def test_generate_alpha_strings(value):
    assert len(value) == 43
```

You can also get random types of strings by excluding the second argument:

```python
@pytest.mark.gen_string(4)
def test_generate_alpha_strings(value):
    assert len(value) > 0
```

Imagine you have a generator function that generate values

```python
from pytest_fauxfactory import GenString

def get_values():
    yield 'custom_value'
    yield GenString('alpha', length=12)
    yield GenString('html', length=12)
    yield GenString('utf8', length=12)

@pytest.mark.gen_string(1, get_values)
def test_generate_from_generator(value):
    assert len(value) > 10
```
will generate 4 tests

```shell
tests/test_pytest_fauxfactory.py::test_generate_from_generator[custom_value] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_generator[ESvaxoCXdoRq] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_generator[<strike>DQqTVYVRuVlR</strike>] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_generator[\u1271\u942e\u8be2\U00024c23\U00020990\u0e0d\u688b\ucf1b\u4370\U000223ff\uba9e\u3dd7] PASSED
```

Generating tests with a list

```python
from pytest_fauxfactory import GenString

list_values = [
    GenString('alpha', length=12),
    GenString('utf8', length=12),
]


@pytest.mark.gen_string(1, list_values)
def test_generate_from_list(value):
    """Generate from generator expression"""
    assert len(value) > 11
```
will generate 2 tests

```shell
tests/test_pytest_fauxfactory.py::test_generate_from_list[WAnJyPemgqYf] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_list[\U0002f87d\ucda5\u82d9\u448f\u1f45\u51e9\U000260f6\U00028ccd\u0525\U00010a29\u3462\U00013103] PASSED
```

If you want to generate tests from a list of predefined and generated values.
 - Note that we have to pass a generator expression as argument

```python
values = [
    'valid_value_1',
    'valid_value_2',
    'valid_value_3',
    GenString('alpha', length=12),
    GenString('utf8', length=12),
]

@pytest.mark.gen_string(1, (val for val in values))
def test_generate_from_generator_expression(value):
    assert len(value) >= 12
```
Will generate 5 tests for each value in values list

```shell
tests/test_pytest_fauxfactory.py::test_generate_from_generator_expression[valid_value_1] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_generator_expression[valid_value_2] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_generator_expression[valid_value_3] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_generator_expression[bpHXdUJUNdSA] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_generator_expression[\uadbc\u9a8f\ubae5\uba97\ua91a\u95e5\U00025125\ua81b\u495d\ua110\u0d87\U00020b6c] PASSED

```

If we need to generate a test with value as a list of values, we have to pass a
callable as argument

```python
import fauxfactory

@pytest.mark.gen_string(2, fauxfactory.gen_numeric_string, length=24)
def test_gen_something_from_direct_callable(value):
    assert isinstance(value, list)
    assert len(value) == 2
    for gen_value in value:
        assert len(gen_value) == 24
        assert is_numeric(gen_value)
    assert value[0] != value[1]
```
will generate one test with value as a list of values

```shell
tests/test_pytest_fauxfactory.py::test_gen_something_from_direct_callable[value0] PASSED
```

We can also combine all the values sources in a list

```python

def get_values_c():
    yield 'custom_value'
    yield GenString('utf8', length=12)


valid_values_c = [
    'valid_value_1',
    GenString('html', length=12),
]


combined_list = [
    # add gen string with generator
    GenString(get_values_c),
    # add gen string with generator expression that iter over a list
    GenString(val for val in valid_values_c),
    # add a simple gen string from a string
    GenString('alpha', length=12),
    # add a simple gen string from a callable
    GenString(fauxfactory.gen_numeric_string, length=12)
]

@pytest.mark.gen_string(1, combined_list)
def test_generate_from_combined_list(value):
    """Generate from a combined list"""
    if isinstance(value, list):
        # a callable always return a list
        assert len(value[0]) == 12
    else:
        assert len(value) >= 12
```
will generate 6 tests
```shell
tests/test_pytest_fauxfactory.py::test_generate_from_combined_list[custom_value] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_combined_list[\uc89c\U00011194\uc0cd\U00028330\U00021634\u7ae3\U000201dc\U0002ca91\u734f\U000237c8\U0001d723\U00024fb4] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_combined_list[valid_value_1] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_combined_list[<i>NHJGUBXqDgGL</i>] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_combined_list[GLqbZzoJZlpt] PASSED
tests/test_pytest_fauxfactory.py::test_generate_from_combined_list[value5] PASSED

```
 