import os
from dektools.file import list_dir
from dektools.shell import shell_wrapper
from dektools.py import get_whl_name
from .base import InstallerBase, register_installer


@register_installer('whl')
class WhlInstaller(InstallerBase):
    def run(self):
        for whl_file in list_dir(self.path):
            if whl_file.endswith('.whl'):
                shell_wrapper(
                    f'bash -c "python3 -m pip uninstall -y {get_whl_name(whl_file)} 2>&1 || true;'
                    f'python3 -m pip install {whl_file}"'
                )
