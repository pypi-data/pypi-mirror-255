from types import GeneratorType

from pybrary.command import Command, Param, ValidationError


class MethodParam(Param):
    '''Method
    Target or Manager method or attribute
    '''
    name = 'method'
    positional = True

    def verify(self, value):
        target = self.get('target')

        if hasattr(target, value):
            method = getattr(target, value)
            return method

        if ':' in value:
            meth, _, val = value.partition(':')
        else:
            meth = value

        for key in ('system', 'Package', 'Service'):
            manager = target.managers[key]
            if hasattr(manager, meth):
                method = getattr(manager, meth)
                if callable(method):
                    return method
                else:
                    self.set('manager', manager)
                    return value

        raise ValidationError(f'Invalid method "{value}" for target "{target}"')


class MethodCmd(Command):
    '''method
    Execute target method
    or get/set target attribute
    '''
    Params = [
        MethodParam,
    ]
    vargs = True
    shortcut = True

    def run(self):
        target = self.get('target')
        method = self.get('method')
        if callable(method):
            result = method(*self.args, **self.kws)
            if isinstance(result, GeneratorType):
                for vals in result:
                    print('\t'.join(map(str, vals)))
            else:
                print(result)
        else:
            manager = self.get('manager')
            name = '.'.join(str(manager).split('.')[1:])
            if ':' in method:
                attr, _, val = method.partition(':')
                val1 = getattr(manager, attr)
                setattr(manager, attr, val)
                val2 = getattr(manager, attr)
                if val2 != val1:
                    print(f'    {name}.{attr}:{val1} -> {val2}')
            else:
                value = getattr(manager, method)
                print(f'    {name}.{method} == {value}')

