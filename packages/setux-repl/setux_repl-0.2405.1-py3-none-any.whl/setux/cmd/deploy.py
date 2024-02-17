from pybrary.command import Command, Param, ValidationError


class ModuleParam(Param):
    '''Module
    Setux Module
    '''
    name = 'module'
    positional = True

    def verify(self, name):
        target = self.get('target')
        if name in target.modules.items:
            return name
        raise ValidationError(f'Module {name} not found')


class DeployCmd(Command):
    '''deploy
    Deploy Module
    '''
    Params = [
        ModuleParam,
    ]
    vargs = True
    shortcut = True

    def run(self):
        target = self.get('target')
        name = self.get('module')
        module = target.modules.items[name]

        if self.args:
            m = "module's arguments must be keyword arguments\n"
            print(f'\n ! invalid argument : {" ".join(self.args)} !\n ! {m}')
            return

        k = {k:v for k,v in self.kws.items() if not k.startswith('_')}
        if name=='infos': k['report'] = 'quiet'
        try:
            target.deploy(name, **k)
        except KeyError as x:
            key = x.args[0]
            print(f'\n ! missing argument : {key}  !\n')
