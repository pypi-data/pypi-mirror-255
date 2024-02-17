from pybrary.command import Command


class Sh(Command):
    '''Run shell cmd on target.
    '''
    line = True

    def run(self):
        target = self.get('target')
        line = self.get('_line_')
        target(line)
