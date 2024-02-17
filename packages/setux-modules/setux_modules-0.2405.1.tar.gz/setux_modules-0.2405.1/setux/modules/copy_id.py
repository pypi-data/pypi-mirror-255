from setux.core.module import Module


class Distro(Module):
    '''Send Public Key to Target
    kw:
        usr : User name
        pub : Public key
    '''

    def deploy(self, target, **kw):

        usr = kw['usr']
        pub = kw['pub']

        user = target.user(usr)

        path = f'/home/{usr}/.ssh'
        name = f'authorized_keys'
        full = f'{path}/{name}'

        ok = target.dir(
            path, mode='700', user=usr, group=user.group.name
        )

        if not ok:
            return False

        target.send(pub, full)

        ok = target.file(
            full, mode='600', user=usr, group=user.group.name
        )
        return ok
