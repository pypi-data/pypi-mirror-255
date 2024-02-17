from setuptools import setup
from setuptools.command.install import install
import os
import shutil


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        newd = "/opt/extensions"
        if not os.path.exists(newd):
            os.makedirs(newd)
        shutil.copy("lambchop/lc_ext.py", newd)

setup(
    cmdclass = {
        'install': CustomInstallCommand
    }
)