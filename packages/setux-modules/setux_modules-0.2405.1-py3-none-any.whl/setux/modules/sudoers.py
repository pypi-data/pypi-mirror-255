from setux.core.module import Module


# pylint: disable=arguments-differ


class Distro(Module):
    '''Add User to sudoers

    arg:
        user : user name
    '''

    def deploy(self, target, *, user, d=True):

        grp = target.groups.fetch(user)
        grp.add('wheel')

        line = f'{user} ALL=(ALL) NOPASSWD: ALL'
        if d:
            sudoers = f'/etc/sudoers.d/{user}'
            target.write(sudoers, line)
        else:
            sudoers = '/etc/sudoers'
            target.deploy('upd_cfg',
                cfg = sudoers,
                src = f'^{user}',
                dst = line,
                report = 'quiet',
            )

        ok = 'wheel' in grp.get()
        ret, out, err = target.run(f'sudo -l -U {user}')
        ok = ok and '(ALL) NOPASSWD: ALL' in (line.strip() for line in out)

        return ok
