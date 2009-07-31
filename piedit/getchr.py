"""Module to get a character from STDIN across platforms"""
import sys

__author__ = "Steven Anderson"
__copyright__ = "Steven Anderson 2008"
__credits__ = ["Steven Anderson"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Steven Anderson"
__email__ = "steven.james.anderson@googlemail.com"
__status__ = "Production"

def get_chr_unix():
    """Gets a character from STDIN in unix"""
    import tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_chr_windows():
    """Gets a character from STDIN in windows"""
    import msvcrt
    return msvcrt.getch()

def get_chr():
    """Gets a character from STDIN"""
    try:
        return get_chr_unix()
    except ImportError:
        return get_chr_windows()