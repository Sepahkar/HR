from pathlib import Path
import os.path
import pyodbc
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
PARENT_DIR = str(BASE_DIR.parent).replace('\\','\\\\')
DEBUG = True
SECRET_KEY = 'django-insecure-#kkatg$g5w^93x$r8a@2bo*c8scivp8&k0it4_bvjw4197b1go'


ALLOWED_HOSTS = ['192.168.50.15','192.168.20.81','192.168.27.90','192.168.70.83','192.168.27.17','localhost','192.168.70.25','127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'HR.apps.HrConfig',
    'Duties.apps.DutiesConfig',
    'django_middleware_global_request',
    'rest_framework',
    'corsheaders',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_middleware_global_request.middleware.GlobalRequestMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'HR.middleware.DetectUserInfoMiddleware',

]

ROOT_URLCONF = 'Config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,"templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mssql',# 'mssql',
        'NAME': 'HR',
        'USER': 'sa',
        'PASSWORD': 'Master123',
        'HOST': 'EIT-DJANGO-DB\\DJANGODB',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',  # 'SQL Server Native Client 11.0'
        },
    },
    'Duties': {
        'ENGINE': 'mssql',  # 'mssql',
        'NAME': 'HR',
        'USER': 'sa',
        'PASSWORD': 'Master123',
        'HOST': 'EIT-DJANGO-DB\\DJANGODB',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',  # 'SQL Server Native Client 11.0'
        },
    },
    'AccessControl': {
        'ENGINE': 'mssql',  # 'mssql',
        'NAME': 'AccessControl',
        'USER': 'sa',
        'PASSWORD': 'Master123',
        'HOST': 'EIT-DJANGO-DB\\DJANGODB',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server', #'SQL Server Native Client 11.0'
        },
    },
    'EIT': {
        'ENGINE': 'mssql',  # 'mssql',
        'NAME': 'EIT',
        'USER': 'sa',
        'PASSWORD': 'Master123',
        'HOST': 'EIT-DJANGO-DB\\DJANGODB',
        'PORT': '',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',  # 'SQL Server Native Client 11.0'
        },
    },
    'VIR': {
        'ENGINE': 'mssql',  # 'mssql',
        'NAME': 'FAQ',
        'USER': 'sa',
        'PASSWORD': 'Master123',
        'HOST': 'EIT-DJANGO-DB\DJANGODB',
        'PORT': '',
        'OPTIONS': {"driver": "ODBC Driver 17 for SQL Server"},
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# this section append end of every settings.py

STATIC_URL = '/static/'
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR,"static")]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,"media")
STATIC_URL_EIT = '/static_eit/'
STATIC_ROOT_EIT = os.path.join(BASE_DIR.parent,"EIT\static")
MEDIA_URL_HR = '/media_hr/'
MEDIA_ROOT_HR = os.path.join(BASE_DIR.parent,"HR\media")


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DATABASE_ROUTERS = ['DBRouters.router.CustomRouter',]
ROUTERS_APP_DB = {'AccessControl':'AccessControl','HR':'default','Duties':'default' ,'EIT':'EIT'}

AUTHENTICATION_BACKENDS = [
    "HR.backends.LdapBackend",
]

SESSION_COOKIE_NAME = os.getcwd().split("\\")[-1] + '_sessionid'

from django_auth_ldap.config import LDAPSearch
import ldap

AUTH_LDAP_SERVER_URI = "ldap://192.168.20.22:389"
AUTH_LDAP_BIND_DN = 'bpms'
AUTH_LDAP_BIND_PASSWORD = 'Wsxedc@123'
AUTH_LDAP_USER_SEARCH = LDAPSearch("DC=eit,DC=local", ldap.SCOPE_SUBTREE, "(&(objectClass=*)(sAMAccountName=%(user)s))")

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"https://192.168.20.81$",
    r"http://192.168.20.81$",
]
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
CORS_ALLOW_ALL_ORIGINS = True
CURRENT_APP_PORT = "14000"
ACCESSCONTROL_IP_PORT = "http://192.168.20.81:13000"
APP_MODE = "production"
if os.path.exists(os.path.join(BASE_DIR,"Config/local_settings.py")):
    from .local_settings import *
    APP_MODE = "development"
    print("start app in development mode")
else:
    print("your app is production mode")