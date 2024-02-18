import warnings
from string import Formatter
from typing import Any, Callable, Dict, List, Set

from airfold_common.error import AirfoldError, AirfoldKeyError


class StrictFormatter(Formatter):
    """A subclass of formatter that checks for extra keys."""

    def check_unused_args(self, used_args, args, kwargs) -> None:
        """Check to see if extra parameters are passed."""
        extra = set(kwargs).difference(used_args)
        if extra:
            raise AirfoldKeyError(extra)

    def vformat(self, format_string, args, kwargs) -> str:
        """Check that no arguments are provided."""
        if len(args) > 0:
            raise AirfoldError("No arguments should be provided, " "everything should be passed as keyword arguments.")
        return super().vformat(format_string, args, kwargs)

    def validate_input_variables(self, format_string: str, input_variables: List[str]) -> None:
        dummy_inputs = {input_variable: "foo" for input_variable in input_variables}
        super().format(format_string, **dummy_inputs)


class NoStrictFormatter(StrictFormatter):
    def check_unused_args(self, used_args, args, kwargs) -> None:
        """Not check unused args"""
        pass


formatter = StrictFormatter()
no_strict_formatter = NoStrictFormatter()


def jinja2_formatter(template: str, **kwargs: Any) -> str:
    try:
        from minijinja import Template  # type: ignore
    except ImportError:
        raise ImportError(
            "jinja2 not installed, which is needed to use the jinja2_formatter. "
            "Please install it with `pip install jinja2`."
        )

    return Template(template).render(**kwargs)


def _get_fstring_variables_from_template(template: str) -> Set[str]:
    return set([field_name for _, field_name, _, _ in Formatter().parse(template) if field_name is not None])


def _get_jinja2_variables_from_template(template: str) -> Set[str]:
    try:
        from minijinja import Environment, meta
    except ImportError:
        raise ImportError(
            "jinja2 not installed, which is needed to use the jinja2_formatter. "
            "Please install it with `pip install jinja2`."
        )
    env = Environment()
    ast = env.parse(template)
    variables = meta.find_undeclared_variables(ast)
    return variables


def validate_jinja2(template: str, input_variables: List[str]) -> None:
    input_variables_set = set(input_variables)
    valid_variables = _get_jinja2_variables_from_template(template)
    missing_variables = valid_variables - input_variables_set
    extra_variables = input_variables_set - valid_variables

    warning_message = ""
    if missing_variables:
        warning_message += f"Missing variables: {missing_variables} "

    if extra_variables:
        warning_message += f"Extra variables: {extra_variables}"

    if warning_message:
        warnings.warn(warning_message.strip())


DEFAULT_FORMATTER_MAPPING: Dict[str, Callable] = {
    "f-string": formatter.format,
    "jinja2": jinja2_formatter,
}

DEFAULT_VALIDATOR_MAPPING: Dict[str, Callable] = {
    "f-string": formatter.validate_input_variables,
    "jinja2": validate_jinja2,
}

DEFAULT_TEMPLATE_VARIABLES_NAME_GETTER_MAPPING: Dict[str, Callable] = {
    "f-string": _get_fstring_variables_from_template,
    "jinja2": _get_jinja2_variables_from_template,
}


def check_valid_template(template: str, template_format: str, input_variables: List[str]) -> None:
    """Check that template string is valid."""
    if template_format not in DEFAULT_FORMATTER_MAPPING:
        valid_formats = list(DEFAULT_FORMATTER_MAPPING)
        raise AirfoldError(f"Invalid template format. Got `{template_format}`;" f" should be one of {valid_formats}")
    try:
        validator_func = DEFAULT_VALIDATOR_MAPPING[template_format]
        validator_func(template, input_variables)
    except KeyError as e:
        raise AirfoldError("Invalid prompt schema; check for mismatched or missing input parameters. " + str(e))


def get_variables_from_template(template: str, template_format: str) -> Set[str]:
    """Get variables from template string."""
    if template_format not in DEFAULT_TEMPLATE_VARIABLES_NAME_GETTER_MAPPING:
        valid_formats = list(DEFAULT_TEMPLATE_VARIABLES_NAME_GETTER_MAPPING)
        raise AirfoldError(f"Invalid template format. Got `{template_format}`;" f" should be one of {valid_formats}")

    get_variables_func = DEFAULT_TEMPLATE_VARIABLES_NAME_GETTER_MAPPING[template_format]
    return get_variables_func(template)


def format_template(template: str, template_format: str, **kwargs: Any) -> str:
    """Format template string."""
    if template_format not in DEFAULT_FORMATTER_MAPPING:
        valid_formats = list(DEFAULT_FORMATTER_MAPPING)
        raise AirfoldError(f"Invalid template format. Got `{template_format}`;" f" should be one of {valid_formats}")

    formatter_func = DEFAULT_FORMATTER_MAPPING[template_format]
    return formatter_func(template, **kwargs)
