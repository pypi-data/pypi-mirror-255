from pybrary.command import Command, Param, ValidationError

from setux.logger import logger


class Level(Param):
    '''Log Level
    '''
    name = 'log_level'
    positional = True
    default = 'debug'

    def verify(self, level):
        if logger.logs(level):
            return level
        raise ValidationError(f"There's no {level} log")


class Logs(Command):
    '''Show log files.
    '''
    Params = [
        Level,
    ]

    def run(self):
        level = self.get('log_level')
        log = logger.logs(level)
        print(open(log).read())
