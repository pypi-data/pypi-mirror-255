"""functions for converting introspected elements into useful representations"""
import re
import typing
import inspect
import collections
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Optional, Union, TypeVar, Callable

T = TypeVar('T')


DOCSTRING_PARAM_REGEX = re.compile(r'(?:param +)(\w+)(?:: +)((?:\w+| )+)')


def extract_signature(function: Callable[..., Any]) -> Iterable[inspect.Parameter]:
    return inspect.signature(function).parameters.values()


@dataclass
class Parameter:
    """class for keeping function's parameter signature and docstring"""
    name: str
    type_annotation: type[T]
    docstring: Optional[str] = None
    default: Optional[T] = inspect.Parameter.empty

    def __post_init__(self):
        if self.type_annotation is bool and not self.has_default_value:
            raise ValueError('bool field must have an optional value')
        if self.origin == Union:
            if isinstance(self.args, tuple):
                raise ValueError(f'quick_gooey dose not support Optional/Union fields with many possible type values')
            elif self.has_default_value and self.default is not None:
                raise ValueError(f'Optionals with default non None values are inappropriate see https://docs.python.org/3/library/typing.html#typing.Optional')

    @property
    def origin(self) -> Optional[type]:
        origin = typing.get_origin(self.type_annotation)
        if origin is None:
            return None

        is_optional = (
            origin is Union
            and len(self.type_annotation.__args__) == 2
            and self.type_annotation.__args__[1] is type(None)
        )
        return origin if not is_optional else Optional

    @property
    def args(self) -> Optional[type | tuple[type]]:
        args = typing.get_args(self.type_annotation)
        if not args:
            return None
        elif len(args) == 1 or self.origin == Optional:
            return args[0]
        else:
            return args

    @property
    def has_default_value(self):
        return self.default is not inspect.Parameter.empty

    @staticmethod
    def parse_callable_parameters(
        function: Callable[..., Any],
        signature_extractor: Callable[..., Iterable[inspect.Parameter]] = extract_signature,
    ) -> Iterable['Parameter']:
        """
        inspects :function: signature and wraps inspect.Parameter into this class

        :param function: callable to inspect
        :param signature_extractor: method to extract the inspect.Parameter list with
        """
        parameters_docstring = dict(DOCSTRING_PARAM_REGEX.findall(function.__doc__)) if function.__doc__ else {}

        parsed_parameters = []
        for parameter in signature_extractor(function):
            if parameter.name in parameters_docstring:
                docstring = parameters_docstring[parameter.name]
            else:
                docstring = None

            parsed_parameters.append(
                Parameter(
                    name=parameter.name,
                    type_annotation=parameter.annotation,
                    docstring=docstring,
                    default=parameter.default,
                )
            )

        return parsed_parameters

