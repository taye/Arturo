#  _____     _               
# |  _  |___| |_ _ _ ___ ___ 
# |     |  _|  _| | |  _| . |
# |__|__|_| |_| |___|_| |___|
# http://32bits.io/Arturo/
#

import inspect
import sys
import textwrap

from ano import Arduino15
import ano
from ano.Arduino15.commands.base import Command
from ano.Arduino15.commands.init import Init


def _is_command(commandClass):
    if inspect.isclass(commandClass):
        print "okay"
    if inspect.isclass(commandClass) and issubclass(commandClass, Command) and commandClass != Command:
        print "yes"
        return True
    else:
        return False
    
def getAllCommands():
    return inspect.getmembers(sys.modules[__name__], _is_command)
