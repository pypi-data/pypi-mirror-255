from typing import Callable, Any


class CONFIG:
    # root
    RESET = "\033[0m"

    # basic
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright text color escape codes
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_PURPLE = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Text style escape codes
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"

    # Background color escape codes
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_PURPLE = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

    # Bright background color escape codes
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_PURPLE = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"


def with_chameleon(color: str) -> Callable[..., Any]:
    def chameleonize(fn: Callable[..., Any]) -> Any:
        def wrapper(*args, **kwargs):
            val = fn(*args, **kwargs)
            return color + f"{val}" + CONFIG.RESET

        return wrapper

    return chameleonize


class chameleon:
    # basics
    @with_chameleon(color=CONFIG.BLUE)
    def blue(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.GREEN)
    def green(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.YELLOW)
    def yellow(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.WHITE)
    def white(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.PURPLE)
    def purple(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.RED)
    def red(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.CYAN)
    def cyan(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BLACK)
    def black(value: str) -> str:
        return str(value)

    # text styles
    @with_chameleon(color=CONFIG.BOLD)
    def bold(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.UNDERLINE)
    def underline(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.ITALIC)
    def italic(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.STRIKETHROUGH)
    def strikethrough(value: str) -> str:
        return str(value)

    # Bright text color escape codes

    @with_chameleon(color=CONFIG.BRIGHT_BLACK)
    def bright_black(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BRIGHT_RED)
    def bright_red(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BRIGHT_GREEN)
    def bright_green(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BRIGHT_YELLOW)
    def bright_yellow(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BRIGHT_BLUE)
    def bright_blue(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BRIGHT_PURPLE)
    def bright_purple(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BRIGHT_CYAN)
    def bright_cyan(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BRIGHT_WHITE)
    def bright_white(value: str) -> str:
        return str(value)

    # background color escape codes

    @with_chameleon(color=CONFIG.BG_BLACK)
    def bg_black(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_RED)
    def bg_red(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_GREEN)
    def bg_green(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_YELLOW)
    def bg_yellow(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_BLUE)
    def bg_blue(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_PURPLE)
    def bg_purple(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_CYAN)
    def bg_cyan(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_WHITE)
    def bg_white(value: str) -> str:
        return str(value)

    # bright background color escape codes

    @with_chameleon(color=CONFIG.BG_BRIGHT_BLACK)
    def bg_bright_black(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_BRIGHT_RED)
    def bg_bright_red(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_BRIGHT_GREEN)
    def bg_bright_green(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_BRIGHT_YELLOW)
    def bg_bright_yellow(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_BRIGHT_BLUE)
    def bg_bright_blue(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_BRIGHT_PURPLE)
    def bg_bright_purple(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_BRIGHT_CYAN)
    def bg_bright_cyan(value: str) -> str:
        return str(value)

    @with_chameleon(color=CONFIG.BG_BRIGHT_WHITE)
    def bg_bright_white(value: str) -> str:
        return str(value)
