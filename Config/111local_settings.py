import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


HOST = "192.168.70.25"
USER_DB = "sa"
PASSWORD_DB = "Master123"
DATABASES = {
    'default': {
        'ENGINE': 'mssql',# 'mssql',
        'NAME': 'HR',
        'USER': USER_DB,
        'PASSWORD': PASSWORD_DB,
        'HOST': HOST,
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',  # 'SQL Server Native Client 11.0'
        },
    },
    'Duties': {
        'ENGINE': 'mssql',  # 'mssql',
        'NAME': 'HR',
        'USER': USER_DB,
        'PASSWORD': PASSWORD_DB,
        'HOST': HOST,
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',  # 'SQL Server Native Client 11.0'
        },
    },
    'AccessControl': {
        'ENGINE': 'mssql',  # 'mssql',
        'NAME': 'AccessControl',
        'USER': USER_DB,
        'PASSWORD': PASSWORD_DB,
        'HOST': HOST,
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server', #'SQL Server Native Client 11.0'
        },
    },
    'EIT': {
        'ENGINE': 'mssql',  # 'mssql',
        'NAME': 'EIT',
        'USER': USER_DB,
        'PASSWORD': PASSWORD_DB,
        'HOST': HOST,
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',  # 'SQL Server Native Client 11.0'
        },
    },
    'VIR': {
        'ENGINE': 'mssql',  # 'mssql',
        'NAME': 'FAQ',
        'USER': USER_DB,
        'PASSWORD': PASSWORD_DB,
        'HOST': HOST,
        'PORT': '',
        'OPTIONS': {"driver": "ODBC Driver 17 for SQL Server"},
    },
}


STATICFILES_DIRS = [os.path.join(BASE_DIR,"static")]

CURRENT_APP_PORT = "14000"
ACCESSCONTROL_IP_PORT = "http://192.168.70.25:13000"