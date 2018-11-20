import os
import subprocess

def get_version():
    d = os.path.dirname(os.path.realpath(__file__))
    try:
        x = open(os.path.join(d, 'VERSION_STAMP'), 'rb').read().strip().decode()
        if x: return x
    except FileNotFoundError:
        pass
    v = os.path.join(d, '../version.sh')
    ver = subprocess.check_output(v, shell=True).decode().strip()
    if 'fatal' in ver or '\n' in ver:
        return '0'
    return ver

__version__ = get_version()
