from functools import partial

import serial
from inputmodule.cli import find_devs
from inputmodule.inputmodule import ledmatrix as lm


S = partial(serial.Serial, baudrate=115200)

matrix_blank = [[0 for _ in range(34)] for _ in range(9)]
matrix_full = [[255 for _ in range(34)] for _ in range(9)]


def draw_matrix(dev, s, matrix):
    for c, r in enumerate(matrix):
        lm.send_col(dev, s, c, r)
    lm.commit_cols(dev, s)


def assert_matrix(matrix):
    assert len(matrix) == 9, "Matrix height is not 9"
    assert len(matrix[0]) == 34, "Matrix width is not 34"
    for row in matrix:
        assert len(row) == 34, "Row width is not 34"
        assert all([0 <= i <= 255 for i in row]), "Value not in range 0-255"


def clamp(value, min_value=10, max_value=255):
    return max(min(value, max_value), min_value)


def eq(vals, brightness_multiplier=100, min_brightness=10):
    """Display 9 values in equalizer diagram starting from the middle, going up and down.

    Adapted from the Framework Python library.
    """
    assert len(vals) == 9, f"Need 9 values for the equalizer: {vals}"
    bm = clamp(brightness_multiplier / 100, 0, 1)
    matrix = [[0 for _ in range(34)] for _ in range(9)]

    for col, val in enumerate(vals[:9]):
        row = int(34 / 2)
        above = int(val / 2)
        below = val - above

        for i in range(above):
            matrix[col][row + i] = clamp(round(val / 34 * 255 * bm), min_value=min_brightness)
        for i in range(below):
            matrix[col][row - 1 - i] = clamp(round(val / 34 * 255 * bm), min_value=min_brightness)

    return matrix


def calculate_brightness(
    percent,
    position,
    length,
    min_value,
    max_value,
    inverted=False,
    percent_impacts_brighness=False,
):
    """
    Calculate the brightness at a given position on a gradient line.

    :param position: The position along the line (0 to length).
    :param length: The total length of the gradient line.
    :param min_value: The minimum gradient value (brightness at the start of the line).
    :param max_value: The maximum gradient value (brightness at the end of the line).
    :param inverted: If True, the gradient is inverted (brightness decreases along the line).
    :return: The brightness at the given position.
    """

    def apply_percent(brightness):
        if percent_impacts_brighness:
            return round(brightness * (percent / 100))
        return round(brightness)

    assert position >= 0, "Position must be greater than or equal to 0"
    if position < 0:
        position = 0
    elif position >= length:
        return apply_percent(max_value) if not inverted else min_value

    ratio = position / length

    if inverted:
        brightness = max_value - ratio * (max_value - min_value)
    else:
        brightness = min_value + ratio * (max_value - min_value)

    return apply_percent(brightness)


def status_vert(
    matrix,
    percent,
    start_col=0,
    width=1,
    brightness=None,
    top_down=False,
    brightness_match_percent=False,
    gradient_func=None,
):
    assert start_col + width <= 9, "Column out of range"
    assert width > 0, "Width must be greater than 0"
    assert not (
        brightness and brightness_match_percent
    ), "Can't set both brightness and brightness_match_percent"
    assert not brightness or 0 <= brightness <= 255, "Brightness not in range 0-255"

    if not brightness and not brightness_match_percent:
        brightness = 255
    elif brightness_match_percent:
        brightness = int(255 * (percent / 100))
    if not gradient_func and not brightness_match_percent:
        gradient_func = lambda x, *args: brightness
    elif not gradient_func and brightness_match_percent:
        gradient_func = lambda x, *args: percent

    if top_down:
        r = range(34)
    else:
        r = range(34, 0, -1)
    col = [
        gradient_func(percent, pixel - 1, 34) if pixel - 1 <= percent / 3 else 0
        # gradient_func(percent, pixel - 1, 34)
        for pixel in r
    ]
    for i in range(start_col, start_col + width):
        matrix[i] = col
    return matrix


def print_matrix(matrix, number=False):
    """Inverts Matrix to print it out"""

    def shape(value):
        if number:
            return f"{value:3}"
        match value:
            case 0:
                return " "
            case _ if value > 224:
                return "█"
            case _ if value > 192:
                return "█"
            case _ if value > 160:
                return "▆"
            case _ if value > 128:
                return "▅"
            case _ if value > 96:
                return "▃"
            case _ if value > 64:
                return "▂"
            case _ if value <= 64:
                return "▁"
            case _:
                return "?"

    for i in range(34):
        print(
            " ".join([shape(matrix[j][i]) if matrix[j][i] else "   " for j in range(9)])
        )
