from setux.core.module import Module


class Distro(Module):
    '''Setux self test

    - test deploy
    - test remote
    - test run
    - test REPL
    '''

    def deploy(self, target, **kw):

        target.deploy('infos')
        target.pip.install('setux_plus')
        target.remote('infos')
        target.pip.install('setux_repl')
        target('setux infos')

        return True
