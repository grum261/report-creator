#!/bin/bash
source /home/ubuntu/.local/share/virtualenvs/report-creator-OjfmrmoB/bin/activate
exec gunicorn --config "/home/ubuntu/prog/python/report-creator/reports/gunicorn_config.py" reports.wsgi
