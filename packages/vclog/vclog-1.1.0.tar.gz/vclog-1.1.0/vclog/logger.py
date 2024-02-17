codes: dict[str, str] = {
    "end": "\x1b[0m",
    "line_up": "\x1b[1A",
    "line_clear": "\x1b[2K",
}

styles: dict[str, str] = {
    "bold": "\x1b[1m",
    "dim": "\x1b[2m",
    "italic": "\x1b[3m",
    "underline": "\x1b[4m",
    "blink": "\x1b[5m",
    "highlight": "\x1b[7m",
    "hidden": "\x1b[8m",
    "strikethrough": "\x1b[9m",
    "double_underline": "\x1b[21m",
}

colors: dict[str, str] = {
    "black": "\x1b[30m",
    "red": "\x1b[31m",
    "green": "\x1b[32m",
    "yellow": "\x1b[33m",
    "blue": "\x1b[34m",
    "magenta": "\x1b[35m",
    "cyan": "\x1b[36m",
    "white": "\x1b[37m",

    "bg_black": "\x1b[40m",
    "bg_red": "\x1b[41m",
    "bg_green": "\x1b[42m",
    "bg_yellow": "\x1b[43m",
    "bg_blue": "\x1b[44m",
    "bg_magenta": "\x1b[45m",
    "bg_cyan": "\x1b[46m",
    "bg_white": "\x1b[47m",

    "secondary_black": "\x1b[90m",
    "secondary_red": "\x1b[91m",
    "secondary_green": "\x1b[92m",
    "secondary_yellow": "\x1b[93m",
    "secondary_blue": "\x1b[94m",
    "secondary_magenta": "\x1b[95m",
    "secondary_cyan": "\x1b[96m",
    "secondary_white": "\x1b[97m",

    "bg_secondary_black": "\x1b[100m",
    "bg_secondary_red": "\x1b[101m",
    "bg_secondary_green": "\x1b[102m",
    "bg_secondary_yellow": "\x1b[103m",
    "bg_secondary_blue": "\x1b[104m",
    "bg_secondary_magenta": "\x1b[105m",
    "bg_secondary_cyan": "\x1b[106m",
    "bg_secondary_white": "\x1b[107m",
}


def format(text: str,
           color: str | None = None,
           bg_color: str | None = None,
           style: str | list[str] | None = None,
           ) -> str:
    """
    Format the text with the given color, background color and style. Check the documentation for the list of colors and styles.

    Arguments
    ---------
    text : str
        The text to be formatted.
    color : str, optional
        The color to be used for the text.
    bg_color : str, optional
        The background color to be used for the text.
    style : str or list[str], optional
        The style to be used for the text.

    Returns
    -------
    str
        The formatted text.
    """
    color_code: str = colors.get(str(color), "")
    text = color_code + text + codes["end"] if color_code else text

    bg_color_code: str = colors.get("bg_"+str(bg_color), "")
    text = bg_color_code + text + codes["end"] if bg_color_code else text

    if style is not None:
        if isinstance(style, str):
            style = [style]

        for s in style:
            style_code: str = styles.get(s, "")
            text = style_code + text + codes["end"] if style_code else text

    return text


def _logger_print(*messages,
                  color: str | None,
                  bg_color: str | None,
                  style: str | list[str] | None,
                  flush: bool,
                  sep: str = " ",
                  end: str = "\n",
                  prefix: str = "",
                  ) -> None:
    result: str = ""

    if isinstance(messages[0], Logger):
        result += f"[{messages[0].name}] "
        messages = messages[1:]

    result += sep.join(map(str, messages))
    result = format(result, color, bg_color, style)

    print(prefix+result, end=end)
    if flush:
        print(codes["line_up"], end=codes["line_clear"])


class ContextAware:
    def __init__(self, method):
        self.method = method

    def __get__(self, instance, _):
        if instance is None:
            return self.method
        return lambda *args, **kwargs: self.method(instance, *args, **kwargs)


INFO_PREFIX: str = format("|I| ", color="green", style="bold")
DEBUG_PREFIX: str = format("|D| ", color="blue", style="bold")
WARNING_PREFIX: str = format("|W| ", color="yellow", style="bold")
ERROR_PREFIX: str = format("|E| ", color="red", style="bold")


class Logger:
    """
    The `Logger` class is a simple class that provides a way to print colored and styled messages to the console.

    It can be used in two ways: it can be instanced to give the logger a name, or it can be used as a static class.

    When instanced, the logger will print the name of the instance before the message.

    When used as a static class, the logger will not print the name of the instance before the message.

    The `Logger` class provides the following methods:
    - `plain`: prints a message with the given color, background color and style.
    - `info`: prints a message to the info level.
    - `debug`: prints a message to the debug level.
    - `warning`: prints a message to the warning level.
    - `error`: prints a message to the error level.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the logger with a name.

        Arguments
        ---------
        name : str
            The name of the logger.
        """
        self.name: str = name

    @ContextAware
    @staticmethod
    def plain(*messages,
              color: str | None = None,
              bg_color: str | None = None,
              style: str | list[str] | None = None,
              flush: bool = False,
              sep: str = " ",
              end: str = "\n",
              ) -> None:
        """
        Print a message with the given color, background color and style. Check the documentation for a list of possible colors and styles, or check the `colors` and `styles` dictionaries of the file.

        Arguments
        ---------
        messages : Any
            The messages to be printed.
        color : str, optional
            The color to be used for the text.
        bg_color : str, optional
            The background color to be used for the text.
        style : str or list[str], optional
            The style to be used for the text.
        flush : bool, optional
            Wether to keep the message in a single line or not.
        sep : str, optional
            The separator to be used between the messages.
        end : str, optional
            The character to be used at the end of the message.
        """

        _logger_print(
            *messages,
            color=color,
            bg_color=bg_color,
            style=style,
            flush=flush,
            sep=sep,
            end=end,
            prefix="",
        )

    @ContextAware
    @staticmethod
    def info(*messages,
             flush: bool = False,
             sep: str = " ",
             end: str = "\n",
             ) -> None:
        """
        Print a message to the info level.

        Arguments
        ---------
        messages : Any
            The messages to be printed.
        flush : bool, optional
            Wether to keep the message in a single line or not.
        sep : str, optional
            The separator to be used between the messages.
        end : str, optional
            The character to be used at the end of the message.
        """

        _logger_print(
            *messages,
            color="green",
            bg_color=None,
            style=None,
            flush=flush,
            sep=sep,
            end=end,
            prefix=INFO_PREFIX,
        )

    @ContextAware
    @staticmethod
    def debug(*messages,
              flush: bool = False,
              sep: str = " ",
              end: str = "\n",
              ) -> None:
        """
        Print a message to the debug level.

        Arguments
        ---------
        messages : Any
            The messages to be printed.
        flush : bool, optional
            Wether to keep the message in a single line or not.
        sep : str, optional
            The separator to be used between the messages.
        end : str, optional
            The character to be used at the end of the message.
        """

        _logger_print(
            *messages,
            color="blue",
            bg_color=None,
            style=None,
            flush=flush,
            sep=sep,
            end=end,
            prefix=DEBUG_PREFIX,
        )

    @ContextAware
    @staticmethod
    def warning(*messages,
                flush: bool = False,
                sep: str = " ",
                end: str = "\n",
                ) -> None:
        """
        Print a message to the warning level.

        Arguments
        ---------
        messages : Any
            The messages to be printed.
        flush : bool, optional
            Wether to keep the message in a single line or not.
        sep : str, optional
            The separator to be used between the messages.
        end : str, optional
            The character to be used at the end of the message.
        """

        _logger_print(
            *messages,
            color="yellow",
            bg_color=None,
            style=None,
            flush=flush,
            sep=sep,
            end=end,
            prefix=WARNING_PREFIX,
        )

    @ContextAware
    @staticmethod
    def error(*messages,
              flush: bool = False,
              sep: str = " ",
              end: str = "\n",
              ) -> None:
        """
        Print a message to the error level.

        Arguments
        ---------
        messages : Any
            The messages to be printed.
        flush : bool, optional
            Wether to keep the message in a single line or not.
        sep : str, optional
            The separator to be used between the messages.
        end : str, optional
            The character to be used at the end of the message.
        """

        _logger_print(
            *messages,
            color="red",
            bg_color=None,
            style=None,
            flush=flush,
            sep=sep,
            end=end,
            prefix=ERROR_PREFIX,
        )
