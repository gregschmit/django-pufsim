
GITVER=$(git describe --tags --long --always | sed 's/v//g' | sed 's/-g.*//g' | sed 's/-/\.dev/g')
GITCHANGED=$(git diff-index --quiet HEAD -- || echo '+changed')

echo $GITVER$GITCHANGED
