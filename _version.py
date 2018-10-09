import os
import subprocess

def get_version():
    d = os.path.dirname(os.path.realpath(__file__)) # resolve symlinks
    return subprocess.check_output(d + '/pufsim/version.sh', shell=True, cwd=d).decode().strip()
