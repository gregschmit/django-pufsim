import os
import subprocess

def get_version():
    d = os.path.dirname(os.path.realpath(__file__)) # resolve symlinks
    return subprocess.run(d + '/pufsim/version.sh', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
