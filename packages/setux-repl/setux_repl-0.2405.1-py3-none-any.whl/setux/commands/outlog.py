from pybrary.command import Command


class OutLog(Command):
    '''Show commands logs.
    '''
    def run(self):
        target = self.get('target')
        log = target.outlog
        print(open(log).read())
