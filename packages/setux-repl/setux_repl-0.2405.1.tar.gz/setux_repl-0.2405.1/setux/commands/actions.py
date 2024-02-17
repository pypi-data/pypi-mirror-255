from pybrary.command import Command, Param


class Pattern(Param):
    '''Filter pattern
    '''
    name = 'actions_pattern'
    positional = True


class Actions(Command):
    '''List Actions
    '''
    Params = [
        Pattern,
    ]

    def run(self):
        target = self.get('target')
        pattern = self.get('actions_pattern')
        actions = target.actions.items
        print('actions')
        print('-------')
        width = len(max(actions.keys(), key=len))+4
        for name, action in sorted(actions.items()):
            hlp = action.help()
            first = hlp.split('\n')[0]
            if (
                not pattern
                or pattern in name
                or pattern in first.lower()
            ): print(f'{name:>{width}} {first}')
