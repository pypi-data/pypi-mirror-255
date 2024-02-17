from pybrary.command import Command, Param, ValidationError


class ActionParam(Param):
    '''Action
    Setux Action
    '''
    name = 'action'
    positional = True

    def verify(self, name):
        target = self.get('target')
        action = target.actions.items.get(name)
        if not action:
            raise ValidationError(f'Action {name} not found')
        return action


class ActionCmd(Command):
    '''action
    Execute Action
    '''
    Params = [
        ActionParam,
    ]
    shortcut = True
    vargs = True

    def run(self):
        target = self.get('target')

        if self.args:
            m = "action's arguments must be keyword arguments\n"
            print(f'\n ! invalid argument : {" ".join(self.args)} !\n ! {m}')
            return

        kws = {k:v for k,v in self.kws.items() if not k.startswith('_')}
        config = ((k,v) for k,v in self.parent.config.items() if k!='target')

        action = self.get('action')(target, **kws)
        action.context.update(config)
        action()

