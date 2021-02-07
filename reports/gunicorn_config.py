command = '/home/ubuntu/.local/share/virtualenvs/report-creator-OjfmrmoB/gunicorn'
pythonpath = '/home/ubuntu/prog/python/report-creator/reports'
bind = '127.0.0.1:8002'
workers = 3
user = 'ubuntu'
limit_request_fields = 32000
limit_request_fields_size = 0
raw_env = 'DJANGO_SETTINGS_MODULE=reports.settings'
