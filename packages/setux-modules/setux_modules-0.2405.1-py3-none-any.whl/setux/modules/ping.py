from setux.core.module import Module


class Distro(Module):
    '''Check Target Reachability
    '''

    register = 'ping'

    def deploy(self, target, **kw):
        pong = kw.get('pong', 'pong')
        ret, out, err = target.run('echo', pong, report='verbose')
        response = out[0]
        return response==pong


class Debian(Distro):
    def deploy(self, target, **kw):
        return super().deploy(target, pong='Debian')


class FreeBSD(Distro):
    def deploy(self, target, **kw):
        return super().deploy(target, pong='FreeBSD')
