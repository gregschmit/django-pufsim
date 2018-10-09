
GITVER=$(git describe --tags --long --always)
GITCHANGED=$(git diff-index --quiet HEAD -- || echo '-changed')

echo $GITVER$GITCHANGED
