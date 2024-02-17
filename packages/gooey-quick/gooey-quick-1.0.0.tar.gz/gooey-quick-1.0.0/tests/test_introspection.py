from inspect import Parameter
from typing import Optional, Literal

import pytest

from gooey_quick.types import FileWithExtension
from gooey_quick.introspection import Parameter as ParameterTested


def some_function(foo: str, bar: int, foobar: float):
    """This function does something
        :param foo: an argument
        :param bar: another argument
        :param foobar: yet another argument
        :returns: None
    """
    pass


def some_function_without_docstring(foo: str, bar: int, foobar: float = 1.2):
    pass


def some_function_with_partial_docstring(foo: str, bar: int, foobar: float = 1.2):
    """This function does something
        :param foo: an argument
        :param bar: another argument
        :returns: None
    """
    pass

@pytest.mark.parametrize('function, expected_parameters', [
    (
        some_function,
        [
            ParameterTested(name='foo', type_annotation=str, docstring='an argument'),
            ParameterTested(name='bar', type_annotation=int, docstring='another argument'),
            ParameterTested(name='foobar', type_annotation=float, default=1.2, docstring='yet another argument'),
        ],
    ),
    (
        some_function_without_docstring,
        [
            ParameterTested(name='foo', type_annotation=str),
            ParameterTested(name='bar', type_annotation=int),
            ParameterTested(name='foobar', type_annotation=float, default=1.2),
        ],
    ),
    (
        some_function_with_partial_docstring,
        [
            ParameterTested(name='foo', type_annotation=str, docstring='an argument'),
            ParameterTested(name='bar', type_annotation=int, docstring='another argument'),
            ParameterTested(name='foobar', type_annotation=float, default=1.2),
        ],
    ),
])
def test_parse_callable_parameters_parses_properly(function, expected_parameters):
    def mock_function_inspector(function):
        return [
            Parameter(
                'foo',
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=str,
            ),
            Parameter(
                'bar',
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=int,
            ),
            Parameter(
                'foobar',
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=float,
                default=1.2,
            ),
        ]

    assert ParameterTested.parse_callable_parameters(
        function,
        signature_extractor=mock_function_inspector,
    ) == expected_parameters



@pytest.mark.parametrize('name, type_annotation, default', [
    (
        'bool_field_no_default',
        bool,
        Parameter.empty,
    ),
    (
        'optional_field_more_than_one_types',
        Optional[str | int],
        Parameter.empty,
    ),
    (
        'optional_field_more_than_one_types',
        Optional[str | int | float],
        Parameter.empty,
    ),
    (
        'optional_field_with_default_non_null_value',
        Optional[str | int],
        'test',
    ),
])
def test_invalid_parameters_dont_parse(name, type_annotation, default):
    with pytest.raises(ValueError):
        ParameterTested(name, type_annotation, 'some docstring', default=default)


@pytest.mark.parametrize('type_annotation, expected_origin', [
    (str, None),
    (int, None),
    (bool, None),
    (float, None),
    (Optional[str], Optional),
    (dict[str, int], dict),
    (list[str], list),
    (tuple[str], tuple),
    (FileWithExtension[Literal['json']], FileWithExtension),
])
def test_parameter_knows_its_origin(type_annotation, expected_origin):
    assert ParameterTested('field_name', type_annotation, default=None).origin == expected_origin


@pytest.mark.parametrize('type_annotation, expected_args', [
    (str, None),
    (int, None),
    (bool, None),
    (float, None),
    (Optional[str], str),
    (dict[str, int], (str, int)),
    (list[str], str),
    (tuple[str], str),
    (FileWithExtension[Literal['json']], Literal['json']),
])
def test_parameter_knows_its_args(type_annotation, expected_args):
    assert ParameterTested('field_name', type_annotation, default=None).args == expected_args
