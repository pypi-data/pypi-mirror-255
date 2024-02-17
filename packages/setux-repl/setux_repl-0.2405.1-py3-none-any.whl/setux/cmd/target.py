from os.path import expanduser

from pybrary.command import Param, ValidationError
from pybrary.ssh import ParamSSH

from setux.targets import Local, SSH


class TargetParam(Param):
    '''Target
    SSH or Local Host
    '''
    name = 'target'
    positional = True
    mandatory = True
    default = 'local'

    def verify(self, value):
        outdir = self.get('outdir') or expanduser('~/setux')

        if value=='local':
            return Local(outdir=outdir)

        try:
            host = ParamSSH(self).validate(value)
        except ValidationError:
            raise ValidationError(f'{value} is not a valid target')

        target = SSH(
            name   = value,
            host   = value,
            outdir = outdir,
        )

        if not target or not target.cnx:
            raise ValidationError(f'{value} is unreachable')

        return target
