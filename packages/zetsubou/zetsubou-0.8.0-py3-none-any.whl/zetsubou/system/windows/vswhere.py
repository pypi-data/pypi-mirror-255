import os

from zetsubou.utils.subprocess import call_process

def find_vswhere():
    executable_name = 'vswhere.exe'
    default_installator_path = 'Microsoft Visual Studio/Installer'
    paths = [
        os.path.join(os.environ['ProgramW6432'], default_installator_path),
        os.path.join(os.environ['ProgramFiles(x86)'], default_installator_path)
    ]

    for path in paths:
        local_path = os.path.join(path, executable_name)
        if os.path.exists(local_path):
            return local_path

    return None

def call_vswhere(executable: str):
    args = [
        executable,
        '-prerelease',
        '-format', 'json', '-utf8'
    ]
    out, err = call_process(args, capture=True, realtime=False)
    if err is not None:
        return None
    return out
