import os
from .settings import AWS_S3_CUSTOM_DOMAIN

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DEBUG = False
SERVER_PORT = '8000'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('AWS_RDS_DB'),
        'USER': os.getenv('AWS_RDS_USERNAME'), 
        'PASSWORD': os.getenv('AWS_RDS_PW'),
        'HOST': os.getenv('AWS_RDS_HOST'),
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'sql_mode': 'STRICT_ALL_TABLES',
        },
    }
}

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    os.getenv('HOST_IP_ADDRESS'),
    AWS_S3_CUSTOM_DOMAIN,
]
