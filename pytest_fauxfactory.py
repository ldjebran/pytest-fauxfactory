# -*- coding: utf-8 -*-
"""Provides FauxFactory helper methods."""
from inspect import isgeneratorfunction, isgenerator
from itertools import chain

import fauxfactory
import pytest
import six
from six.moves import range

STRING_TYPES = (
    'alpha',
    'alphanumeric',
    'cjk',
    'html',
    'latin1',
    'numeric',
    'utf8',
    'punctuation',
)


class GenStringNotFoundError(Exception):
    """Raised when no GenString instance found"""


class GenString(object):
    """fauxfactory string generator helper"""
    __slots__ = ['str_type', 'args', 'kwargs']

    def __init__(self, str_type, *args, **kwargs):
        if str_type is None:
            str_type = fauxfactory.gen_choice(STRING_TYPES)

        if (not isinstance(str_type, six.string_types)
                and not callable(str_type) and not isgenerator(str_type)):
            raise ValueError(
                'str_type must be a string, callable or generator')

        if (isinstance(str_type, six.string_types)
                and str_type not in STRING_TYPES):
            raise ValueError(
                '{0} is not a supported string type. Valid string types'
                ' are {1}.'.format(str_type, u','.join(STRING_TYPES))
            )

        self.str_type = str_type
        self.args = args
        self.kwargs = kwargs

    def get_value(self, value=None):
        """return the corresponding real value of value"""
        if value is None:
            value = self
        if isinstance(value, GenString):
            new_value = list(value())
            if len(new_value) == 1:
                return list(value())[0]
            return new_value
        return value

    def __call__(self, items=1):
        """return values generator"""
        if callable(self.str_type) and isgeneratorfunction(self.str_type):
            for _ in range(items):
                for value in self.str_type():
                    yield self.get_value(value)
        elif callable(self.str_type):
            yield [self.str_type(*self.args, **self.kwargs)
                   for _ in range(items)]
        elif isgenerator(self.str_type):
            for _ in range(items):
                for value in self.str_type:
                    yield self.get_value(value)
        else:
            for _ in range(items):
                yield fauxfactory.gen_string(
                    self.str_type, *self.args, **self.kwargs)


def pytest_generate_tests(metafunc):
    """Parametrize tests using `gen_string` mark."""
    if hasattr(metafunc.function, 'gen_string'):
        # We should have at least the first 2 arguments to gen_string
        args = metafunc.function.gen_string.args
        if len(args) == 0:
            args = (1, 'alpha')
        elif len(args) == 1:
            args = (args[0], 'alpha')
        items, str_type = args
        if not isinstance(items, int):
            raise pytest.UsageError(
                'Mark expected an integer, got a {}: {}'.format(
                    type(items), items))
        if items < 1:
            raise pytest.UsageError(
                'Mark expected an integer greater than 0, got {}'.format(
                    items))
        kwargs = metafunc.function.gen_string.kwargs
        if isinstance(str_type, GenString):
            data = str_type(items=items)
        elif isinstance(str_type, (tuple, list)):
            # always expect that the list is a list of GenString
            data = list(chain.from_iterable(
                gn(items=items)
                for gn in str_type
                if isinstance(gn, GenString)
            ))
            if not data:
                raise GenStringNotFoundError('no GenString found')
        elif (isinstance(str_type, six.string_types) or callable(str_type)
              or isgenerator(str_type)):
            data = GenString(str_type, *args[2:], **kwargs)(items)
        else:
            raise GenStringNotFoundError(
                'no gen string type found to be applied: ({})'
                .format(type(str_type))
            )

        metafunc.parametrize('value', data)
