"""converters from Parameter into arg dict for gooey.GooeyParser.add_argument"""
from enum import Enum
from pathlib import Path
from argparse import Action
from datetime import date, time
from typing import Optional, Any, Union

from gooey_quick.introspection import Parameter
from gooey_quick.types import DirectoryPath, SaveToPath, FileWithExtension


def convert_optional(parameter: Parameter) -> dict[str, Any]:
    return {
        **DEFAULT_TYPE_INTERPRETATION[parameter.type_annotation],
        'required': False,
    }


def convert_file_with_extension(parameter: Parameter) -> dict[str, Any]:
    allowed_file_types = '|'.join((f'{filetype.upper()} (*.{filetype})|*.{filetype}' for filetype in parameter.args))
    allowed_file_types += '|All files (*.*)|*.*'
    return {
        'type': FileWithExtension,
        'widget': 'FileChooser',
        'gooey_options': {
            'wildcard': allowed_file_types,
        },
    }


def convert_list(parameter: Parameter) -> dict[str, Any]:
    if parameter.type_annotation is Path:
        return {
            'type': Path,
            'nargs': '+',
            'widget': 'MultiFileChooser',
        }
    elif parameter.origin is FileWithExtension:
        return {
            **convert_file_with_extension(
                Parameter(
                    parameter.name,
                    parameter.args,
                    parameter.docstring,
                    parameter.default,
                )
            ),
            'widget': 'MultiFileChooser',
            'nargs': '+',
        }
    else:
        raise ValueError(f'list of {parameter.type_annotation} cannot be translated into a Gooey widget!')


def convert_enum(parameter: Parameter) -> dict[str, Any]:
    return {
        'action': StoreEnumAction,
        'type': parameter.type_annotation,
        'choices': [possibility.name for possibility in parameter.type_annotation],
    }


DEFAULT_ORIGIN_CONVERTERS = {
    list:               convert_list,
    Optional:           convert_optional,
    FileWithExtension:  convert_file_with_extension
}


DEFAULT_TYPE_INTERPRETATION = {
    str: {
        'type': str,
    },
    int: {
        'type': int,
        'widget': 'IntegerField',
    },
    bool: {
        'action': 'store_true',
        'required': False,
    },
    float: {
        'type': float,
        'widget': 'DecimalField',
    },
    date: {
        'type': date.fromisoformat,
        'widget': 'DateChooser',
    },
    time: {
        'type': time.fromisoformat,
        'widget': 'TimeChooser',
    },
    Path: {
        'type': Path,
        'widget': 'FileChooser',
        'gooey_options': {
            'wildcard': "All files (*.*)|*.*",
        },
    },
    SaveToPath: {
        'type': SaveToPath,
        'widget': 'FileSaver',
    },
    DirectoryPath: {
        'type': DirectoryPath,
        'widget': 'DirChooser',
    },
}


DEFAULT_SUBTYPES_CONVERTERS = {
    Enum: convert_enum,
}


def convert_to_argument(parameter: Parameter | Optional[Any]):
    """
    converts a parameter into dict of args for gooey.GooeyParser.add_argument

    :param parameter: parameter to be converted
    :raises ValueError: if parameter cannot be translated into a gooey widget
    :returns: dict of args to be passed int gooey.GooeyParser.add_argument
    """

    args = {
        'dest': parameter.name,
        'metavar': parameter.name.capitalize().replace('_', ' '),
        'required': True,
        'action': 'store',
        'help': parameter.docstring,
    }

    if parameter.has_default_value:
        stringify_default = (
            parameter.default is not None
            and parameter.type_annotation not in {int, float, str, bool}
        )
        args['gooey_options'] = {
            'initial_value': str(parameter.default) if stringify_default else parameter.default
        }

    try:
        if parameter.origin in DEFAULT_ORIGIN_CONVERTERS:
            convert = DEFAULT_ORIGIN_CONVERTERS[parameter.origin]
            type_specific_args = convert(
                Parameter(
                    parameter.name,
                    parameter.args,
                    docstring=parameter.docstring,
                    default=parameter.default,
                )
            )
        elif parameter.type_annotation in DEFAULT_TYPE_INTERPRETATION:
            type_specific_args = DEFAULT_TYPE_INTERPRETATION[parameter.type_annotation]
        else:
            for parent_type in DEFAULT_SUBTYPES_CONVERTERS:
                if issubclass(parameter.type_annotation, parent_type):
                    convert = DEFAULT_SUBTYPES_CONVERTERS[parent_type]
                    type_specific_args = convert(parameter)
                    break
            else:
                raise KeyError()
    except KeyError:
        raise ValueError(f'{parameter.type_annotation} cannot be translated into a Gooey widget!')

    try:
        gooey_options = type_specific_args['gooey_options']
        type_specific_args['gooey_options'] = {**gooey_options, **args['gooey_options']}
    except KeyError:
        pass

    return {**args, **type_specific_args}


class StoreEnumAction(Action):
    def __init__(self, *args, **kwargs):
        self.enum_type = kwargs.pop('type')
        super().__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self.enum_type[values])

