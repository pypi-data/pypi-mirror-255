from setux.core.module import Module
from setux.logger import error


class Distro(Module):
    '''Download File

    kw:
        url : File's URL
        dst : File's Dest (defaults to "downloaded"
    '''

    register = 'download'

    @property
    def label(self):
        return 'Download'

    def deploy(self, target, **kw):
        url = kw['url']
        dst = kw.get('dst', 'downloaded')

        try:
            ret, out, err = target.run(f'wget2 -q {url} -O {dst}')
            if ret!=0:
                raise RuntimeError
        except:
            try:
                # curl >= 7.75
                ret, out, err = target.run(f'curl -sfL -w "%{{errormsg}}\n" {url} -o {dst}')
                if ret!=0:
                    raise RuntimeError
            except:
                try:
                    ret, out, err = target.run(f'http --download {url} -o {dst}')
                    if ret!=0:
                        raise RuntimeError
                except:
                    target.Package.install('wget')
                    ret, out, err = target.run(f'wget -q {url} -O {dst}')
                    if ret!=0:
                        msg = err[0]
                        error(msg)
                        raise RuntimeError(msg)
        return True

