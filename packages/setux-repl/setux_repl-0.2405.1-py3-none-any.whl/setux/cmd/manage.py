from types import GeneratorType

from pybrary.command import Command, Param, ValidationError


class ManagerParam(Param):
    '''Manager
    Setux Manager
    '''
    name = 'manager'
    positional = True

    def verify(self, value):
        target = self.get('target')
        if value in target.managers:
            return value
        raise ValidationError(f'Manager {value} not found')


class ActionParam(Param):
    '''Action
    Manager Action
    '''
    name = 'action'
    positional = True

    def verify(self, value):
        return value


class ManageCmd(Command):
    '''manage
    Manager command
    '''
    Params = [
        ManagerParam,
        ActionParam,
    ]
    vargs = True
    shortcut = True

    def run(self):
        target = self.get('target')
        name = self.get('manager')
        action = self.get('action')
        manager = getattr(target, name)

        if ':' in action:
            attr, _, val = action.partition(':')
            setattr(manager, attr, val)
        else:
            action = getattr(manager, action)
            if callable(action):
                result = action(*self.args)
                if isinstance(result, GeneratorType):
                    for vals in result:
                        print('\t'.join(vals))
                else:
                    print(result)
            else:
                print(action)
