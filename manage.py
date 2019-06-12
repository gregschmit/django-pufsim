#!/usr/bin/env python3
"""
Proxy python3 script for the ``manage.py`` in the ``pufsim`` package.
"""
import os
import subprocess
import sys

if __name__ == "__main__":
    # get this directory
    d = os.path.dirname(os.path.abspath(__file__))

    # set the dev directory env variable
    os.environ["DJANGO_PUFSIM_DEVPATH"] = d

    # spawn the app manage.py
    args = sys.argv.copy()
    args[0] = os.path.join(d, 'pufsim/manage.py')
    args.insert(0, sys.executable)
    print("REPO LEVEL EXECUTION\ncwd: {}".format(d))
    print("argv: {}\nspawning...".format(str(args)))
    r = subprocess.run(
        args,
        stdout=sys.stdout.fileno(),
        stderr=sys.stderr.fileno(),
        stdin=sys.stdin.fileno(),
        cwd=d,
    )
