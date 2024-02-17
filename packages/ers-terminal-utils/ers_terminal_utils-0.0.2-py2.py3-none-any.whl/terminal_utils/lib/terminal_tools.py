""" Module for utils from UNIX terminal """
from __future__ import print_function

import sys
import tty
import termios


class KeyboardKeys:
    """ Mapping of keyboard keys """
    ESCAPE = chr(27)
    CONTROL= ESCAPE +'['

    CRTL_C = chr(3)  # CTRL+C
    CRTL_D = chr(4)  # CTRL+D
    CRTL_X = chr(24) # CTRL+X

    ARROW_UP = CONTROL + 'A'
    ARROW_DOWN = CONTROL + 'B'
    PAGE_UP = CONTROL + '5~'
    PAGE_DOWN = CONTROL + '6~'

    ENTER = '\x0D'
    KEY_Q = 'q'
    BACKSPACE = '\x7f'
    ESCAPE = '\x1b'
    TAB = '\t'
    SPACE = ' '
    BACK = '\b'
    DELETE = CONTROL + '3~'
    HOME = CONTROL + 'H'
    END = CONTROL + 'F'
    INSERT = CONTROL + '2~'
    F1 = '\x1bOP'
    F2 = '\x1bOQ'
    F3 = '\x1bOR'
    F4 = '\x1bOS'
    F5 = CONTROL + '15~'
    F6 = CONTROL + '17~'
    F7 = CONTROL + '18~'


class Colors:
    """ Colors for terminal """
    BLUE = '\033[94m'
    DEFAULT = '\033[99m'
    GREY = '\033[90m'
    YELLOW = '\033[93m'
    BLACK = '\033[90m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    MAGENTA ='\033[95m'
    WHITE ='\033[97m'
    RED = '\033[91m'

    HEADER = MAGENTA
    OKBLUE = BLUE
    OKCYAN = CYAN
    OKGREEN = GREEN
    WARNING = YELLOW
    FAIL = RED

    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class InvalidColorError(Exception):
    """ Raised when a invalid color is send """
    def __init__(self, color):
        self.color = color
        self.message = 'Color \'{}\' is not available'.format(color)
        if sys.version_info[0] < 3:
            super(InvalidColorError, self).__init__(self.message)
        else:
            super().__init__(self.message)


class ColorPrint:
    """ Print text on terminal with color

    Raises
    ------
    InvalidColorError
        Raised when a invalid color is send
    """
    AVAILABLE_COLORS = [ color for color in dir(Colors) if color.isupper() ]

    def __call__(self, txt, color='DEFAULT', bold=False, underline=False, end='\n'):
        if not color.upper() in self.AVAILABLE_COLORS:
            raise InvalidColorError(color)

        print_msg = getattr(Colors, color.upper())
        if bold:
            print_msg += Colors.BOLD
        if underline:
            print_msg += Colors.UNDERLINE

        print_msg += txt + Colors.ENDC
        print(print_msg, end=end)


class GetchUnix:
    """ Get a character from the terminal """
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch

if __name__ == '__main__':
    pass
