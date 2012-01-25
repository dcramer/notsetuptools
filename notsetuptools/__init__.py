from distutils import log
from distutils.errors import DistutilsError
from setuptools import setup as setuptools_setup
from setuptools.command.develop import develop as _develop
from setuptools.command.install import install as _install
import os.path
import pkg_resources

__all__ = ('setup',)


class install(_install):
    def finalize_options(self):
        _install.finalize_options(self)
        self.single_version_externally_managed = True


class develop(_develop):
    def initialize_options(self):
        _develop.initialize_options(self)
        self.install_dir = None

    def finalize_options(self):
        _develop.finalize_options(self)

        ei = self.get_finalized_command("egg_info")
        if ei.broken_egg_info:
            raise DistutilsError(
            "Please rename %r to %r before using 'develop'"
            % (ei.egg_info, ei.broken_egg_info)
            )
        basename = pkg_resources.Distribution(
            None, None, ei.egg_name, 'current'
        ).egg_name() + '.egg-info'
        self.target = os.path.join(self.install_dir, basename)
        self.outputs = [self.target]

    def run(self):
        _develop.run(self)
        self.install_namespaces()

    def install_namespaces(self):
        nsp = self._get_all_ns_packages()

        if not nsp:
            return
        filename, ext = os.path.splitext(self.target)
        filename += '-nspkg.pth'
        self.outputs.append(filename)
        log.info("Installing %r", filename)
        if not self.dry_run:
            f = open(filename, 'wt')
            eggbase = os.path.abspath(self.egg_base)
            for pkg in nsp:
                pth = tuple(pkg.split('.'))
                trailer = '\n'
                if '.' in pkg:
                    trailer = (
                        "; m and setattr(sys.modules[%r], %r, m)\n"
                        % ('.'.join(pth[:-1]), pth[-1])
                    )
                f.write(
                    "import sys,types,os; "
                    "p = os.path.join(%(eggbase)r, "
                        "*%(pth)r); "
                    "ie = os.path.exists(os.path.join(p,'__init__.py')); "
                    "m = sys.modules.setdefault(%(pkg)r,types.ModuleType(%(pkg)r)); "
                    "mp = (m or []) and m.__dict__.setdefault('__path__',[]); "
                    "(p not in mp) and mp.append(p)%(trailer)s"
                    % dict(
                        eggbase=eggbase,
                        pth=pth,
                        pkg=pkg,
                        trailer=trailer,
                    )
                )
            f.close()

    def _get_all_ns_packages(self):
        nsp = {}
        for pkg in self.distribution.namespace_packages or []:
            pkg = pkg.split('.')
            while pkg:
                nsp['.'.join(pkg)] = 1
                pkg.pop()
        nsp = list(nsp)
        nsp.sort()  # set up shorter names first
        return nsp


def setup(*args, **kwargs):
    if 'cmdclass' not in kwargs:
        kwargs['cmdclass'] = {}
    kwargs['cmdclass'].setdefault('develop', develop)
    kwargs['cmdclass'].setdefault('install', install)
    setuptools_setup(*args, **kwargs)
