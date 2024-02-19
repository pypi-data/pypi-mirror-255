from typing import Literal

COLOR_LITERAL = Literal[
    "BLACK", "RED", "GREEN", "YELLOW", "BLUE", "PURPLE", "CYAN", "WHITE"
]
BG_COLOR_LITERAL = Literal[
    "BG_BLACK",
    "BG_RED",
    "BG_GREEN",
    "BG_BLUE",
    "BG_PURPLE",
    "BG_CYAN",
    "BG_WHITE",
    "BG_YELLOW",
]


class CONFIG:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # styles
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"

    # backgrounds
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_PURPLE = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def get_color(color: COLOR_LITERAL) -> str:
    if color == "BLACK":
        return CONFIG.BLACK
    if color == "RED":
        return CONFIG.RED
    if color == "BLUE":
        return CONFIG.BLUE
    if color == "WHITE":
        return CONFIG.WHITE
    if color == "GREEN":
        return CONFIG.GREEN
    if color == "CYAN":
        return CONFIG.CYAN
    if color == "PURPLE":
        return CONFIG.PURPLE
    if color == "YELLOW":
        return CONFIG.YELLOW

    return ""


def get_bg(bg: BG_COLOR_LITERAL) -> str:
    if bg == "BG_BLACK":
        return CONFIG.BG_BLACK
    if bg == "BG_RED":
        return CONFIG.BG_RED
    if bg == "BG_BLUE":
        return CONFIG.BG_BLUE
    if bg == "BG_WHITE":
        return CONFIG.BG_WHITE
    if bg == "BG_GREEN":
        return CONFIG.BG_GREEN
    if bg == "BG_CYAN":
        return CONFIG.BG_CYAN
    if bg == "BG_PURPLE":
        return CONFIG.BG_PURPLE
    if bg == "BG_YELLOW":
        return CONFIG.BG_YELLOW

    return ""
