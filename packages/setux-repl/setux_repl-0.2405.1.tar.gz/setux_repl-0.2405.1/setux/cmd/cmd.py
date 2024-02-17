from pybrary.command import Command

from setux.core.plugins import Plugins
import setux.commands


class Commands(Plugins):
    def parse(self, mod, plg, plugin):
        name = '.'.join(mod.split('.')[2:])
        return name, plugin


def get_commands():
    return Commands(
        '_none_', Command, setux.commands
    ).items


class CommandCmd(Command):
    '''Commands
    '''
    subs = {
        name: cmd()
        for name, cmd in get_commands().items()
    }

