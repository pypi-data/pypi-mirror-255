from pybrary.command import Command, Param


class Pattern(Param):
    '''Filter pattern
    '''
    name = 'modules_pattern'
    positional = True


class Modules(Command):
    '''List modules.
    '''
    Params = [
        Pattern,
    ]

    def run(self):
        target = self.get('target')
        pattern = self.get('modules_pattern')
        modules = target.modules.items
        print('modules')
        print('-------')
        width = len(max(modules.keys(), key=len))+4
        for name, mod in sorted(modules.items()):
            hlp = mod.help()
            first = hlp.split('\n')[0]
            if (
                not pattern
                or pattern in name
                or pattern in first.lower()
            ): print(f'{name:>{width}} {first}')
