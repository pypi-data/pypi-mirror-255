from pybrary.command import Command


class Sudo(Command):
    '''Run shell cmd as root.
    '''
    line = True

    def run(self):
        target = self.get('target')
        line = self.get('_line_')
        target(line, sudo='root')
