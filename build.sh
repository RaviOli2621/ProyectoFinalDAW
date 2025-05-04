#!/usr/bin/env bash
# exit on error
set -o errexit

# pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py setup_scheduled_tasks

# python manage.py migrate