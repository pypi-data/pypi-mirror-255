from setux.core.module import Module


class Distro(Module):
    '''Minimum System Requieremnts
    '''

    def do_deploy(self, target, **kw):
        return self.install(target,
            pkg = 'tmux vim',
        )


class Debian(Distro):
    def do_deploy(self, target, **kw):
        return self.install(target,
            pkg = 'pip setuptools venv',
        )


class FreeBSD_13(Distro):
    def do_deploy(self, target, **kw):
        return self.install(target,
            pkg = 'sudo bash python rust',
        )


class Fedora(Distro):
    def do_deploy(self, target, **kw):
        ok = self.install(target,
            pkg = '''
                langpacks-fr
                langpacks-en
                glibc-all-langpacks
            ''',
        )
        if ok:
            ret, out, err = self.run('localectl set-locale LANG=fr_FR.UTF-8')
            ok = ret == 0
        return ok
