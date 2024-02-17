"""wrappers around Gooey that inspect callables"""
import inspect
from typing import Callable, Any, TypeVar

from gooey import GooeyParser, Gooey

from gooey_quick.introspection import Parameter
from gooey_quick import converters

T = TypeVar('T')


def create_parser(function: callable, parser: GooeyParser = None):
    """
    Crate a GooeyParser from a callabe

    :param function: callable to inspect for arguments
    :param parser: base parser
    :returns: a GooeyParser
    """
    if parser is None:
        parser = GooeyParser()

    for args in map(
        converters.convert_to_argument,
        Parameter.parse_callable_parameters(function)
    ):
        parameter_name = args['dest']
        if args.pop('required'):
            parser.add_argument(
                **args,
            )
        else:
            parser.add_argument(
                f'--{parameter_name}',
                **args,
            )

    return parser


def create_sectioned_parser(
    sections: dict[str, Callable[..., Any]],
    base_parser = None,
):
    """
    Transforms :sections: into subparsed GooeyParser

    :param sections: the keys of this dict will be become display names,
    while the values define application logic
    :param base_parser: root parser
    """
    if base_parser is None:
        base_parser = GooeyParser()

    subparser = base_parser.add_subparsers()
    for section_name, handler in sections.items():
        section_parser = subparser.add_parser(
            handler.__name__,
            prog=section_name,
        )
        create_parser(handler, parser=section_parser).set_defaults(handler=handler)

    return base_parser


def run_gooey(
    description: Callable[..., T] | dict[str, Callable[..., Any]],
    **kwargs,
) -> T | Any:
    """
    Transforms :description: into a Gooey program

    :param description: if a callable is provided, Gooey will be started
    in basic and the callable will be called started with the inputted
    parameters. A dict of callables should be transfomed into an advanced
    mode Gooey program, its keys will become sidebars display names while its
    values what's the subprogram's logic
    :param kwargs: keyword arguments that will be passed on to gooey.Gooey.
    See https://github.com/chriskiehl/Gooey#global-configuration
    """
    if callable(description):
        def inner():
            argv = create_parser(description).parse_args()
            return description(**argv.__dict__)
    elif isinstance(description, dict):
        def inner():
            argv = create_sectioned_parser(description).parse_args().__dict__
            return argv.pop('handler')(**argv)
    else:
        raise ValueError(
            f'{description} of {type(description)} cannot be handeled by gooey_quick. '
             'Please pass either a callable or a dict to run_gooey'
        )
    return Gooey(inner, **kwargs)()

