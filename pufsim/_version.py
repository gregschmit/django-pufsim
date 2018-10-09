import subprocess

def get_version():
    return subprocess.run('./version.sh', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
