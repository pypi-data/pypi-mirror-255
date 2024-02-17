from pybrary.command import Command, Param

from setux.core.package import CommonPackager


class Pattern(Param):
    '''Filter pattern
    '''
    name = 'mappings_pattern'
    positional = True


class Mappings(Command):
    '''List mappings.
    '''
    Params = [
        Pattern,
    ]

    def run(self):
        target = self.get('target')
        pattern = self.get('mappings_pattern')
        width = 0
        packages = target.pkgmap
        if packages:
            print('packages :')
            width = len(max(packages.keys(), key=len))+4
            for name, pkg in sorted(packages.items()):
                if (
                    not pattern
                    or pattern in name
                    or pattern in pkg
                ): print(f'{name:>{width}} {pkg}')

        for manager in target.managers.values():
            if isinstance(manager, CommonPackager):
                packages = manager.pkgmap
                if packages:
                    print(f'{manager.manager} :')
                    w = len(max(packages.keys(), key=len))+4
                    width = max(width, w)
                    for name, pkg in sorted(packages.items()):
                        if (
                            not pattern
                            or pattern in name
                            or pattern in pkg
                        ): print(f'{name:>{width}} {pkg}')

        services = target.svcmap
        if services:
            print('\nservices :')
            w = len(max(services.keys(), key=len))+4
            width = max(width, w)
            for name, svc in sorted(services.items()):
                if (
                    not pattern
                    or pattern in name
                    or pattern in svc
                ): print(f'{name:>{width}} {svc}')
