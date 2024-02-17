from os import environ
from subprocess import run

from pybrary.command import Command, Param, ValidationError
from pybrary import bash

from setux.core.action import Action
from setux.core.manage import Manager
from setux.core.module import Module
from setux.cli.usage import usage
from ..cmd.cmd import get_commands


help = '''
actions [pattern]
    list available actions

commands [pattern]
    list available commands

managers [pattern]
    list available managers

modules [pattern]
    list available modules

mappings [pattern]
    list available mappings

help "action"
    show "action" help

help "commad"
    show "command" help

help "manager"
    show "manager" help

help "module"
    show "module" help
'''


class Obj(Param):
    '''name
    '''
    name = 'help_obj'
    positional = True

    def verify(self, name):
        target = self.get('target')
        commands = get_commands()
        if name in commands:
            return commands[name]()

        obj = target.actions.items.get(name)
        if obj: return obj

        obj = target.managers.get(name)
        if obj: return obj

        obj = target.modules.items.get(name)
        if obj: return obj(target.distro)

        raise ValidationError(f"{name} not found")


def header(txt):
    print(txt)
    print('-'*len(txt))


class Help(Command):
    '''Show Help.
    '''
    Params = [
        Obj,
    ]

    def run(self):
        obj = self.get('help_obj')
        if not obj:
            tmp = '/tmp/usage'
            with open(tmp, 'w') as out:
                out.write(usage())
            pager = environ['PAGER']
            run([pager, tmp])
            return

        target = self.get('target')
        '''
        if version_info >= (3, 10):
            match obj:
                case Command() as command:
                    header(f'Command {command.__class__.__name__}')
                    command.help(fetch=False)
                case Manager() as manager:
                    header(f'{manager}'.replace('.', ' '))
                    manager.help()
                case Module() as module:
                    header(f'Module {module.__module__.split(".")[-1]}')
                    module.help()
                case _:
                    print(usage)
        else:
        '''
        if isinstance(obj, Command):
            command = obj
            header(f'Command {command.__class__.__name__}')
            print(command.help(fetch=False))
        elif isinstance(obj, Manager):
            manager = obj
            header(f'{manager}'.replace('.', ' '))
            print(manager.help())
        elif isinstance(obj, Module):
            module = obj
            header(f'Module {module.__module__.split(".")[-1]}')
            print(module.help())
        elif issubclass(obj, Action):
            action = obj
            header(f'{action.__name__}')
            print(action.help())
        else:
            print(help)

