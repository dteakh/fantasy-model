import re

from parsing.common import FantasyError


def _get_placement(placement: str) -> float:
    """
    Function parses placement on event and returns average number.
    :param placement: placement string on event.
    :return: corresponding floating value
    """
    pattern = r"\d+"
    numbers = re.findall(pattern, placement)
    numbers = [float(s) for s in numbers]

    if len(numbers) == 0:
        raise FantasyError.invalid_arguments(f"placement = '{placement}'")

    return sum(numbers) / len(numbers)


def _get_intensity(match):
    return match["rounds_won"] / match["rounds_lost"]


def _is_enum_instance(enum_class, variable):
    try:
        enum_class(variable)
    except ValueError:
        return False
    return True
