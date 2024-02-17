from enum import Enum
from pathlib import Path
from typing import Optional, Literal
from datetime import date, time

import pytest

from gooey_quick import converters
from gooey_quick.introspection import Parameter
from gooey_quick.converters import StoreEnumAction
from gooey_quick.types import DirectoryPath, SaveToPath, FileWithExtension

PARAMETER_DOCSTRING = 'some docstring for a parameter'


class ExampleEnum(Enum):
    ONE = 1
    TWO = 2


@pytest.mark.parametrize(
    'parameter, expected_add_argument_args',
    [
        (
            Parameter(
                'file_field',
                type_annotation=Path,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='file_field',
                action='store',
                type=Path,
                widget='FileChooser',
                gooey_options=dict(wildcard='All files (*.*)|*.*'),
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='File field',
            ),
        ),
        (
            Parameter(
                'file_field_optional_value',
                type_annotation=Path,
                docstring=PARAMETER_DOCSTRING,
                default=Path('home/'),
            ),
            dict(
                dest='file_field_optional_value',
                action='store',
                type=Path,
                widget='FileChooser',
                gooey_options=dict(
                    wildcard='All files (*.*)|*.*',
                    initial_value=str(Path('home/')),
                ),
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='File field optional value',
            ),
        ),
        (
            Parameter(
                'choice_field_from_enum',
                type_annotation=ExampleEnum,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='choice_field_from_enum',
                action=StoreEnumAction,
                type=ExampleEnum,
                choices=[enum.name for enum in ExampleEnum],
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Choice field from enum',
            ),
        ),
        (
            Parameter(
                'choice_field_from_enum_default_value',
                type_annotation=ExampleEnum,
                docstring=PARAMETER_DOCSTRING,
                default=ExampleEnum.ONE.name,
            ),
            dict(
                dest='choice_field_from_enum_default_value',
                action=StoreEnumAction,
                type=ExampleEnum,
                choices=[enum.name for enum in ExampleEnum],
                gooey_options={
                    'initial_value': ExampleEnum.ONE.name,
                },
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Choice field from enum default value',
            ),
        ),
        (
            Parameter(
                'int_field',
                type_annotation=int,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='int_field',
                action='store',
                type=int,
                widget='IntegerField',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Int field',
            ),
        ),
        (
            Parameter(
                'int_field_default_value',
                type_annotation=int,
                docstring=PARAMETER_DOCSTRING,
                default=1,
            ),
            dict(
                dest='int_field_default_value',
                action='store',
                type=int,
                gooey_options={
                    'initial_value': 1,
                },
                widget='IntegerField',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Int field default value',
            ),
        ),
        (
            Parameter(
                'float_field',
                type_annotation=float,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='float_field',
                action='store',
                type=float,
                widget='DecimalField',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Float field',
            ),
        ),
        (
            Parameter(
                'float_field_default_value',
                type_annotation=float,
                docstring=PARAMETER_DOCSTRING,
                default=1.2,
            ),
            dict(
                dest='float_field_default_value',
                action='store',
                type=float,
                gooey_options={
                    'initial_value': 1.2,
                },
                widget='DecimalField',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Float field default value',
            ),
        ),
        (
            Parameter(
                'bool_field_default_true',
                type_annotation=bool,
                docstring=PARAMETER_DOCSTRING,
                default=True,
            ),
            dict(
                dest='bool_field_default_true',
                action='store_true',
                required=False,
                help=PARAMETER_DOCSTRING,
                metavar='Bool field default true',
                gooey_options={
                    'initial_value': True,
                }
            ),
        ),
        (
            Parameter(
                'bool_field_default_false',
                type_annotation=bool,
                docstring=PARAMETER_DOCSTRING,
                default=False,
            ),
            dict(
                dest='bool_field_default_false',
                action='store_true',
                required=False,
                help=PARAMETER_DOCSTRING,
                metavar='Bool field default false',
                gooey_options={
                    'initial_value': False,
                }
            ),
        ),
        (
            Parameter(
                'date_field',
                type_annotation=date,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='date_field',
                action='store',
                type=date.fromisoformat,
                widget='DateChooser',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Date field',
            ),
        ),
        (
            Parameter(
                'date_field_default_value',
                type_annotation=date,
                docstring=PARAMETER_DOCSTRING,
                default=date(year=2002, month=7, day=22),
            ),
            dict(
                dest='date_field_default_value',
                action='store',
                type=date.fromisoformat,
                gooey_options={
                    'initial_value': str(date(year=2002, month=7, day=22)),
                },
                widget='DateChooser',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Date field default value',
            ),
        ),
        (
            Parameter(
                'time_field',
                type_annotation=time,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='time_field',
                action='store',
                type=time.fromisoformat,
                widget='TimeChooser',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Time field',
            ),
        ),
        (
            Parameter(
                'time_field_default_value',
                type_annotation=time,
                docstring=PARAMETER_DOCSTRING,
                default=time(hour=21, minute=37, second=10),
            ),
            dict(
                dest='time_field_default_value',
                action='store',
                type=time.fromisoformat,
                gooey_options={
                    'initial_value': str(time(hour=21, minute=37, second=10)),
                },
                widget='TimeChooser',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Time field default value',
            ),
        ),
        (
            Parameter(
                'string_field',
                type_annotation=str,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='string_field',
                action='store',
                type=str,
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='String field',
            ),
        ),
        (
            Parameter(
                'string_field_default_value',
                type_annotation=str,
                docstring=PARAMETER_DOCSTRING,
                default='test',
            ),
            dict(
                dest='string_field_default_value',
                action='store',
                type=str,
                gooey_options={
                    'initial_value': 'test',
                },
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='String field default value',
            ),
        ),
        (
            Parameter(
                'optional_field',
                type_annotation=Optional[str],
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='optional_field',
                action='store',
                type=str,
                required=False,
                help=PARAMETER_DOCSTRING,
                metavar='Optional field',
            ),
        ),
        (
            Parameter(
                'optional_field_with_none_default',
                type_annotation=Optional[str],
                docstring=PARAMETER_DOCSTRING,
                default=None,
            ),
            dict(
                dest='optional_field_with_none_default',
                action='store',
                type=str,
                required=False,
                help=PARAMETER_DOCSTRING,
                metavar='Optional field with none default',
                gooey_options={
                    'initial_value': None,
                },
            ),
        ),
        (
            Parameter(
                'directory_field',
                type_annotation=DirectoryPath,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='directory_field',
                action='store',
                type=DirectoryPath,
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Directory field',
                widget='DirChooser',
            ),
        ),
        (
            Parameter(
                'directory_optional_field',
                type_annotation=DirectoryPath,
                docstring=PARAMETER_DOCSTRING,
                default=DirectoryPath('/home/jaca/'),
            ),
            dict(
                dest='directory_optional_field',
                action='store',
                type=DirectoryPath,
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Directory optional field',
                gooey_options={
                    'initial_value': str(DirectoryPath('/home/jaca/')),
                },
                widget='DirChooser',
            ),
        ),
        (
            Parameter(
                'save_to_field',
                type_annotation=SaveToPath,
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='save_to_field',
                action='store',
                type=SaveToPath,
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Save to field',
                widget='FileSaver',
            ),
        ),
        (
            Parameter(
                'save_to_default_field',
                type_annotation=SaveToPath,
                docstring=PARAMETER_DOCSTRING,
                default=SaveToPath('/home/jaca/saveto.txt'),
            ),
            dict(
                dest='save_to_default_field',
                action='store',
                type=SaveToPath,
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='Save to default field',
                gooey_options={
                    'initial_value': str(SaveToPath('/home/jaca/saveto.txt')),
                },
                widget='FileSaver',
            ),
        ),
        (
            Parameter(
                'file_list_field',
                type_annotation=list[Path],
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='file_list_field',
                action='store',
                type=Path,
                nargs='+',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='File list field',
                widget='MultiFileChooser',
            ),
        ),
        (
            Parameter(
                'file_with_certain_filetype',
                type_annotation=FileWithExtension[Literal['csv', 'json']],
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='file_with_certain_filetype',
                action='store',
                type=FileWithExtension,
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='File with certain filetype',
                widget='FileChooser',
                gooey_options={
                    'wildcard': '|'.join((
                        'CSV (*.csv)|*.csv',
                        'JSON (*.json)|*.json',
                        'All files (*.*)|*.*'
                    ))
                },
            ),
        ),
        (
            Parameter(
                'file_with_certain_extension_list_field',
                type_annotation=list[FileWithExtension[Literal['csv', 'json']]],
                docstring=PARAMETER_DOCSTRING,
            ),
            dict(
                dest='file_with_certain_extension_list_field',
                action='store',
                type=FileWithExtension,
                nargs='+',
                required=True,
                help=PARAMETER_DOCSTRING,
                metavar='File with certain extension list field',
                widget='MultiFileChooser',
                gooey_options={
                    'wildcard': '|'.join((
                        'CSV (*.csv)|*.csv',
                        'JSON (*.json)|*.json',
                        'All files (*.*)|*.*'
                    ))
                },
            ),
        ),
    ],
    ids=lambda parameter: parameter.name if isinstance(parameter, Parameter) else None,
)
def test_parameter_is_properly_converted(parameter, expected_add_argument_args):
    assert converters.convert_to_argument(parameter) == expected_add_argument_args


@pytest.mark.parametrize('untranslatable_parameter', [
    Parameter(
        'composite_field',
        type_annotation=dict,
        docstring=PARAMETER_DOCSTRING,
        default=dict(x=1),
    ),
    Parameter(
        'composite_optional_field',
        type_annotation=Optional[dict],
        docstring=PARAMETER_DOCSTRING,
    ),
])
def test_parameter_conversion_raises_value_error_if_cant_translate_parameter(untranslatable_parameter):
    with pytest.raises(ValueError):
        converters.convert_to_argument(untranslatable_parameter)

