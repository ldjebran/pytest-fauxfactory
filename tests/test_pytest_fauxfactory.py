# -*- coding: utf-8 -*-
"""Tests the `gen_string` mark."""
import contextlib

import pytest
from pytest_fauxfactory import GenString, STRING_TYPES
import fauxfactory
import six


@contextlib.contextmanager
def assert_raises(exception):
    try:
        yield
    except exception:
        assert True
    else:
        assert False


def is_numeric(value):
    """Check if value is numeric."""
    return value.isnumeric()


def test_mark_plain(testdir):
    """Check that mark `gen_string` adds 10 iterations to test."""
    testdir.makepyfile("""
        import pytest
        @pytest.mark.gen_string(10)
        def test_something(value):
            assert 1 == 1
    """)
    result = testdir.runpytest()
    result.assert_outcomes(passed=10)
    assert result.ret == 0


def test_mark_correct_value(testdir):
    """Check that argument `value` is being used to pass random data."""
    testdir.makepyfile("""
        import pytest
        @pytest.mark.gen_string(10)
        def test_something(value):
            assert value
    """)
    result = testdir.runpytest()
    result.assert_outcomes(passed=10)
    assert result.ret == 0


def test_mark_incorrect_value(testdir):
    """Check that argument `value` is not being used."""
    testdir.makepyfile("""
        import pytest
        @pytest.mark.gen_string(10)
        def test_something(foo):
            assert foo
    """)
    result = testdir.runpytest()
    result.assert_outcomes(error=1)
    assert 'uses no argument \'value\'' in result.stdout.str()
    assert result.ret == 2


def test_mark_incorrect_argument(testdir):
    """Check that first argument to mark is numeric."""
    testdir.makepyfile("""
        import pytest
        @pytest.mark.gen_string('1')
        def test_something(value):
            assert value
    """)
    result = testdir.runpytest()
    result.assert_outcomes(error=1)
    assert 'Mark expected an integer' in result.stdout.str()
    assert result.ret == 2


@pytest.mark.gen_string()
def test_gen_alpha_string_with_no_arguments(value):
    """Passing no arguments should return a random string type."""
    assert len(value) > 0


@pytest.mark.gen_string(1)
def test_gen_alpha_string_with_limit_arguments(value):
    """Passing limit argument should return a random string type."""
    assert len(value) > 0


@pytest.mark.gen_string(4, 'alpha', length=12)
def test_gen_alpha_string_with_length(value):
    """Generate an `alpha` string of length 12."""
    assert len(value) == 12


@pytest.mark.gen_string(
    1,
    'punctuation',
    length=12,
    validator=is_numeric,
    default='1')
def test_gen_alpha_string_with_validator(value):
    """Call `gen_string` with validator that returns default of `1`."""
    assert value == '1'


@pytest.mark.gen_string(2, GenString('alpha', length=12))
def test_gen_string_with_gen_string_instance(value):
    """Generate an `alpha` string of length 12."""
    assert len(value) == 12


def test_gen_string_with_list_gen_string_instances(testdir):
    testdir.makepyfile("""
        import pytest
        from pytest_fauxfactory import GenString
        import fauxfactory

        gen_string_list = [
            GenString('alpha', length=12),
            GenString('html', length=100),
            GenString('utf8', length=24),
            # passing a callable
            GenString(fauxfactory.gen_numeric_string, length=24)
        ]
        @pytest.mark.gen_string(3, gen_string_list)
        def test_something_from_list(value):
            assert 1 == 1
    """)
    result = testdir.runpytest()
    # we have 3 static str_types and passing items = 3
    # the generated tests should be 3 per type eg: 3*3=9
    # we have one callable str_type that will generate one value (a list of 3
    # items), 9 + 1 = 10

    result.assert_outcomes(passed=10)
    assert result.ret == 0


gen_string_list = [
    GenString('alpha', length=12),
    # passing a callable
    GenString(fauxfactory.gen_numeric_string, length=24)
]


@pytest.mark.gen_string(1, gen_string_list)
def test_something_from_gen_string_list(value):
    """Ensure that the needed values are generated"""
    if isinstance(value, list):
        # a callable always return a list
        assert len(value) == 1
        assert len(value[0]) == 24
        assert value[0].isnumeric()
    else:
        assert len(value) == 12
        assert value.isalpha()


@pytest.mark.gen_string(
    2, GenString(fauxfactory.gen_numeric_string, length=24))
def test_gen_something_from_callable(value):
    """generating from callable always return a list of the generated str"""
    assert len(value) == 2
    for gen_value in value:
        assert len(gen_value) == 24
        assert gen_value.isnumeric()
    assert value[0] != value[1]


@pytest.mark.gen_string(2, fauxfactory.gen_numeric_string, length=24)
def test_gen_something_from_direct_callable(value):
    """generating from callable always return a list of the generated str"""
    assert isinstance(value, list)
    assert len(value) == 2
    for gen_value in value:
        assert len(gen_value) == 24
        assert is_numeric(gen_value)
    assert value[0] != value[1]


def simple_function_generator():
    """A simple generator function that yield a generic value and a list of
    values"""
    yield fauxfactory.gen_numeric_string(length=24)
    # passing list as value
    yield ['aa', 'ab']


@pytest.mark.gen_string(1, simple_function_generator)
def test_gen_something_from_generator(value):
    """Check that test functions are properly generated when using a generator
    """
    checked = 0
    if isinstance(value, list):
        assert len(value) == 2
        assert value == ['aa', 'ab']
        checked += 1
    elif isinstance(value, six.string_types):
        assert is_numeric(value)
        assert len(value) == 24
        checked += 1

    assert checked == 1


def test_none_str_type():
    """Check str_type initialization value when str_type is None"""
    gen_string = GenString(None)
    assert gen_string.str_type in STRING_TYPES


def test_invalid_non_string_str_type():
    """Check that ValueError is raised when initialising with str_type that is
    not a string and not callable"""
    with assert_raises(ValueError):
        GenString(fauxfactory.gen_integer())


def test_invalid_str_type():
    """Check that ValueError is raised when initialising with str_type not in
    STRING_TYPES"""
    with assert_raises(ValueError):
        GenString(fauxfactory.gen_string('alpha'))


def test_gen_string_generator():
    """Ensure generator function is handled properly"""
    values = [
        'a',
        'b',
        GenString('alpha', length=10)
    ]

    def gen_values():
        for value in values:
            yield value

    gen_values = list(GenString(gen_values)())
    assert len(gen_values) == 3
    assert 'a' in gen_values
    assert 'b' in gen_values
    gen_values.remove('a')
    gen_values.remove('b')
    # remaining the generated one
    gen_value = gen_values[0]
    assert len(gen_value) == 10
    assert gen_value.isalpha()


def test_gen_string_generator_expression():
    """Ensure generator function is handled properly"""
    values = [
        'a',
        'b',
        GenString('alpha', length=10)
    ]

    gen_values = list(GenString((val for val in values))())
    assert len(gen_values) == 3
    assert 'a' in gen_values
    assert 'b' in gen_values
    gen_values.remove('a')
    gen_values.remove('b')
    # remaining the generated one
    gen_value = gen_values[0]
    assert len(gen_value) == 10
    assert gen_value.isalpha()


def test_gen_string_callbale():
    gen_values = list(
        GenString(fauxfactory.gen_numeric_string, length=10)(2))
    assert len(gen_values) == 1
    values = gen_values[0]
    assert len(values) == 2
    for value in values:
        assert value.isnumeric()
        assert len(value) == 10


def test_gen_string_string():
    gen_values = list(
        GenString('numeric', length=10)(2))
    assert len(gen_values) == 2
    for value in gen_values:
        assert value.isnumeric()
        assert len(value) == 10


def test_invalid_list_generate_test_value(testdir):
    """Check that error is raised when using str_type as a list with invalid
    items"""
    testdir.makepyfile("""
        import pytest

        @pytest.mark.gen_string(1, [1,2])
        def test_something_from_list(value):
            assert 1 == 1
    """)

    result = testdir.runpytest()
    result.assert_outcomes(error=1)
    assert 'no GenString found' in result.stdout.str()
    assert result.ret == 2


def test_invalid_str_type_generate_test_value(testdir):
    """Check that error is raised when using a not valid str_type type"""
    testdir.makepyfile("""
        import pytest

        @pytest.mark.gen_string(1, 2)
        def test_something_from_list(value):
            assert 1 == 1
    """)
    result = testdir.runpytest()
    result.assert_outcomes(error=1)
    assert 'no gen string type found to be applied' in result.stdout.str()
    assert result.ret == 2


list_values = [
    GenString('alpha', length=12),
    GenString('utf8', length=12),
]


@pytest.mark.gen_string(1, list_values)
def test_generate_from_list(value):
    """Generate from list"""
    assert len(value) > 11


valid_values = [
    'valid_value_1',
    'valid_value_2',
    'valid_value_3',
    GenString('alpha', length=12),
    GenString('utf8', length=12),
]


@pytest.mark.gen_string(1, (val for val in valid_values))
def test_generate_from_generator_expression(value):
    """Generate from generator expression"""
    assert len(value) >= 12


def get_values():
    yield 'custom_value'
    yield GenString('alpha', length=12)
    yield GenString('html', length=12)
    yield GenString('utf8', length=12)


@pytest.mark.gen_string(1, get_values)
def test_generate_from_generator(value):
    """Generate from generator"""
    assert len(value) >= 12


def get_values_c():
    yield 'custom_value'
    yield GenString('utf8', length=12)


valid_values_c = [
    'valid_value_1',
    GenString('html', length=12),
]

combined_list = [
    GenString(get_values_c),
    GenString(val for val in valid_values_c),
    GenString('alpha', length=12),
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
