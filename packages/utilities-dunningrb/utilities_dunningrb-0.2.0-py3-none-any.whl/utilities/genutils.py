"""Define general utility methods not easily classified for any of the other
utility modules.
"""

from typing import Any


def convert_to_type(input_value: Any, target_type: Any) -> Any:
    """Convert the given object to the given type. Raises TypeError if the conversion fails.

    Note: For converting type defaultdict to type dict, please see dictutils.get_pure_dict.
    """
    if isinstance(input_value, target_type):
        return input_value

    # Handle special cases, if necessary.

    if isinstance(input_value, str) and isinstance(target_type, list):
        return [input_value]

    try:
        return target_type(input_value)
    except TypeError as e:
        err_msg = f"Failed to convert {input_value} to {target_type}."
        raise TypeError(err_msg) from e
