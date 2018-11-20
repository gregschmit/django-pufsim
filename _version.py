import os
import subprocess
import sys

def get_version():
    d = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'version.sh')
    return subprocess.check_output(d, shell=True).decode().strip()

def stamp_directory(d):
    with open(os.path.join(d, 'VERSION_STAMP'), 'wb') as f:
        f.write(get_version().encode() + b'\n')

def unstamp_directory(d):
    os.remove(os.path.join(d, 'VERSION_STAMP'))
