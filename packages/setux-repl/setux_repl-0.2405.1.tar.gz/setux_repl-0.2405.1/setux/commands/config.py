from os import environ, makedirs
from os.path import expanduser
from pathlib import Path
from subprocess import run

from pybrary import get_app_config
from pybrary.command import Command


init_config = '''
config = dict(
    target = 'local',
)
'''.strip()


def get_config_path():
    return get_app_config('setux')[0]


def get_config():
    return get_app_config('setux')[1]


class ConfigCmd(Command):
    '''Setux Configuration.

    Edit the Setux Config file.
    '''
    def run(self):
        path = get_config_path()
        if not path:
            path = Path('~/.config/setux/config.py').expanduser()
            makedirs(path.parent, exist_ok=True)
            with open(path, 'w') as out:
                out.write(init_config)
        editor = environ.get('EDITOR','vim')
        run([editor, path])

