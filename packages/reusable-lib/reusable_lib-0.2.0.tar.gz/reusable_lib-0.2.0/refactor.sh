#!/bin/bash

yapf --style google -i ./*.py

pip freeze > requirements.txt

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# it fails in an old python
#pylint --rcfile="$SCRIPT_DIR/pylintrc" --output=fix_python.txt ./*.py

pylint --rcfile="$SCRIPT_DIR/pylintrc" ./*.py |tee ./fix_python.txt

shellcheck ./*.sh |tee ./fix_bash.txt
