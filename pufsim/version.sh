#!/bin/sh

# version.sh: gets a PEP440-compliant version

# add useful places to PATH if they aren't there
PATH=$PATH:/usr/local/bin:/usr/bin:/bin

# get and format git version
GITVER=$(git describe --tags --always | sed 's/v//g' | sed 's/-g.*//g' | sed 's/-/\.dev/g')
GITCHANGED=$(git diff-index --quiet HEAD -- || echo '+changed')

# send it
echo $GITVER$GITCHANGED
