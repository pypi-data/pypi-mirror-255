from os import environ
from pathlib import Path
from subprocess import call

from pybrary.command import Command, Param


class Remote(Param):
    '''File to edit
    '''
    name = 'path'
    positional = True
    mandatory = True


class User(Param):
    '''User
    '''
    name = 'user'


class Edit(Command):
    '''Edit a file
    '''
    Params = [
        Remote,
        User,
    ]

    def run(self):
        target = self.get('target')
        remote = self.get('path')
        sudo = self.get('user')
        editor = environ.get('EDITOR','vim')
        dest = Path('/tmp/setux')
        dest.mkdir(exist_ok=True)
        path = Path(remote)
        local = f'{dest}/{path.name}'
        ok = target.fetch(remote, local, sudo=sudo, quiet=True)
        if ok:
            original = open(local).read()
        else:
            original = ''
            with open(local, 'w'): pass
        call([editor, local])
        edited = open(local).read()
        if edited!=original:
            ok = target.write(remote, edited, sudo=sudo)
            status = '.' if ok else 'X'
            print(f'write {remote} {status}')
