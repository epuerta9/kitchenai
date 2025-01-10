#!/bin/bash

cd /app

# Function to check if a package is installed
check_package() {
    $VENV_PATH/bin/python -c "import pkg_resources; pkg_resources.require('$1')" 2>/dev/null
    return $?
}

if [ "$1" = "bash" ] || [ "$1" = "sh" ]; then
    exec "$@"
else
    exec "$@"
fi 