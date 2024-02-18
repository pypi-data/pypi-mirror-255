"""Define utility methods to facilitate user interactions.
"""
import subprocess
import sys
import termios
import tty


def any_key_continue() -> None:
    while True:
        option = get_char()
        if option.lower() == "q":
            confirm_quit()
        else:
            return


def clear_screen() -> None:
    subprocess.run(["clear"])


def confirm_quit() -> None:
    msg = "Are you sure you want to exit? [Y/y] to confirm."
    display_message(msg)
    confirm = get_char()
    if confirm.lower == "y":
        sys.exit()
    else:
        any_key_continue()


def display_message_and_wait(msg: str) -> None:
    clear_screen()
    display_message(msg=msg)
    any_key_continue()


def display_message(msg: str) -> None:
    print(f"\n{'*'*12}\n{msg}\n{'*'*12}\n")


def get_char() -> str:
    """Get character input from the keyboard."""

    def _get_char():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _get_char()


def get_option_as_int() -> int:
    """Get integer option input from keyboard."""
    msg = "<<< Enter option or [Q/q] to quit: >>>"
    display_message(msg)
    option = get_char()
    if option.lower() == "q":
        confirm_quit()
    try:
        option = int(option)
    except ValueError:
        msg = f"Invalid option: {option}."
        display_message(msg=msg)
    else:
        return option


def show_progress_bar(
    iteration: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    length: int = 100,
    fill: str = "█",
    end_char: str = "\r",
) -> None:
    """Create a progress bar at the command line.

    https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    bar_length = int(length * iteration // total)
    bar = fill * bar_length + "-" * (length - bar_length)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=end_char)

    if iteration == total:
        print()
