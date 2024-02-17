from setux.core.module import Module


class Distro(Module):
    '''Set User as sudoer
    kw:
        usr : User name
        pub : Public key

    - Create User if not present
    - Add User to sudoers
    - Send User's public key
    '''

    def deploy(self, target, **kw):

        usr = kw['usr']
        pub = kw['pub']

        ok = target.user(usr)
        ok = ok and target.deploy('sudoers', user=usr)
        ok = ok and target.deploy('copy_id', **kw)

        return ok
