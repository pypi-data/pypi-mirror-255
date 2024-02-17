from re import compile

from setux.core.module import Module
from setux.logger import debug


class Distro(Module):
    '''Update Config File (sed)
    '''

    def deploy(self, target, *, path, line, select=None, sudo=None, user=None, group=None, mode=None):
        cont = self.target.read(path, sudo=sudo, report='quiet')
        msg = [f'{path} <>']
        if select:
            sre = compile(select).search
            updated, found = [], False
            for cur in cont.split('\n'):
                if sre(cur):
                    found = True
                    msg.append(f' <  {cur}')
                    msg.append(f'  > {line}')
                    updated.append(line)
                else:
                    updated.append(cur)
            if not found:
                updated.append(line)
            target.write(path, '\n'.join(updated)+'\n', sudo=sudo, report='quiet')
        else:
            msg.append(f'  > {line}')
            target.write(path, f'{cont}{line}\n', sudo=sudo, report='quiet')

        debug('\n'.join(msg))
        return True
