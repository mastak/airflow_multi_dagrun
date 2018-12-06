#!/usr/bin/env bash

PYTHON_SHORT_VER=$(python3 -c "import sys; print('{}{}'.format(sys.version_info.major, sys.version_info.minor))")

set -e
if [ "$(docker version -f '{{ .Server.Version }}')" \< "1.12" ]; then
    echo "At least Docker 1.12 is required"
    exit 2
fi

if [ $PYTHON_SHORT_VER \< "35" ]; then
    echo "At least Python 3.5 is required"
    exit 2
fi

echo "Creating development environment in './env'"
python3 -m venv env

export SLUGIFY_USES_TEXT_UNIDECODE=yes
env/bin/pip3 install apache-airflow[postgres,crypto,celery]
