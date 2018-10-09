#!/bin/sh

# version.sh: gets a PEP440-compliant version

GITVER=$(git describe --tags --always | sed 's/v//g' | sed 's/-g.*//g' | sed 's/-/\.dev/g')
GITCHANGED=$(git diff-index --quiet HEAD -- || echo '+changed')

echo $GITVER$GITCHANGED
