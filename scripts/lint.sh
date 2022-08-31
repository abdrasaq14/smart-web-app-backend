set -ex

RELEVANT_DIR="src"
isort $RELEVANT_DIR ${CHECK_ONLY}
black $RELEVANT_DIR ${CHECK} --exclude=migrations
flake8 .
