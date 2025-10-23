import traceback
import jwt
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import base64
import datetime
from django.contrib.auth import get_user_model
import pytz
from dotenv import load_dotenv
from django.conf import settings
import ast
from pathlib import Path
import os
from HR.backends import create_not_exists_user
from django.contrib.auth import login
from HR.models import Users
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model


dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=os.path.join(dir,".env"))


def encrypt(data):
    message = str(data).encode("utf-8")
    with open(os.path.join(dir,"public_key.pem")) as f:
        key_data = f.read()
    key = RSA.import_key(key_data)
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(message)
    ciphertext = base64.b64encode(ciphertext)
    return ciphertext


def decrypt(ciphertext):
    ciphertext = base64.b64decode(ciphertext)
    with open(os.path.join(dir,"private_key.pem")) as f:
        key_data = f.read()
    key = RSA.import_key(key_data)
    cipher = PKCS1_OAEP.new(key)
    plaintext = cipher.decrypt(ciphertext)
    last_data = plaintext.decode("utf-8")
    if '{' in last_data:
        last_data = ast.literal_eval(last_data)
    return last_data


def enc_jwt(data):
    encoded = jwt.encode(data, os.getenv('APP_USER_SECRET_KEY'), algorithm="HS256")
    return str(encoded)

def dec_jwt(encrypted):
    try:
        if type(encrypted) is str:
            encrypted = str(encrypted).encode("utf-8")
        data = jwt.decode(encrypted, os.getenv('APP_USER_SECRET_KEY'), algorithms=["HS256"])
        return data
    except:
        return None

def check_is_admin(access):
    ret = False
    try:
        decodeJTW = jwt.decode(access,os.getenv('APP_USER_SECRET_KEY'), algorithms=["HS256"])
        now = int(datetime.datetime.now(pytz.timezone('Asia/Tehran')).timestamp())
        exp = int(decodeJTW['exp'])
        user = decodeJTW['UserName']
        app_name = decodeJTW['AppName']
        if exp > now:
            if get_user_model().objects.filter(username=user, is_superuser=True, is_active=True, is_staff=True).exists():
                ret = True
        if app_name != settings.SESSION_COOKIE_NAME.split("_")[0]:
            ret = False
    except:
        ret = False

    return ret


def init_tokens(user):
    user = str(user).lower()
    decodeJTW = {}
    decodeJTW['UserName'] = user
    decodeJTW['TokenDate'] = int(datetime.datetime.now(pytz.timezone('Asia/Tehran')).timestamp())
    decodeJTW['exp'] = datetime.datetime.now(pytz.timezone('Asia/Tehran')) + datetime.timedelta(minutes=60)
    encoded = enc_jwt(decodeJTW)
    return str(encoded)


def create_cookie_on_response(request,response,access=None):
    user = str(request.user).lower()
    access = init_tokens(user) if access is None else access
    response.set_cookie(
        key='access',
        value=access,
        expires=datetime.timedelta(minutes=45),
        httponly=True,
    )
    return response

def check_access_user_vs_authenticated_user(request,access_user):
    session_name = settings.SESSION_COOKIE_NAME
    session_key = request.COOKIES.get(session_name)
    ret = False
    if session_key:
        try:
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            uid = session_data.get('_auth_user_id')
            user = get_user_model().objects.filter(id=uid).first()
            if user and user.username.lower() == access_user.lower():
                ret = True
        except:
            ret = False
    return ret


def check_is_authenticated(request):
    session_name = settings.SESSION_COOKIE_NAME
    session_key = request.COOKIES.get(session_name)
    ret = False
    if session_key:
        try:
            session = Session.objects.get(session_key=session_key)
            session_data = session.get_decoded()
            uid = session_data.get('_auth_user_id')
            user = get_user_model().objects.filter(id=uid).first()
            if user:
                ret = True
        except:
            ret = False
    return ret

def validate_access_token_and_auth_user(request,access=None):
    try:
        if access is None:
            access = request.COOKIES.get('access')
        decodeJTW = dec_jwt(access)
        if access is None or decodeJTW is None:
            return False,False,''
        now = int(datetime.datetime.now().timestamp())
        exp = int(decodeJTW['exp'])
        user = decodeJTW['UserName']
        if exp > now and user and user != 'none':
            valid_token = True
            new_access = access
            if check_access_user_vs_authenticated_user(request, user) is False:
                login(request, get_object_user(request, user))
            auth_user = True
        elif exp <= now and user and user != 'none':
            valid_token = True
            new_access = init_tokens(user)
            if check_access_user_vs_authenticated_user(request, user) is False:
                login(request, get_object_user(request, user))
            auth_user = True
        else:
            return False, False, ''


        if valid_token and auth_user and new_access and user.lower() in os.getenv('LIST_SUPER_SUPERUSERS').split(','):
            app_user = get_object_user(request, user)
            if app_user.is_superuser is False:
                app_user.is_superuser = True
                app_user.save()
    except:
        traceback.print_exc()
        return False, False, ''

    return valid_token,auth_user,new_access


def validate_access(access):
    try:
        ret = False
        decodeJTW = dec_jwt(access)
        now = int(datetime.datetime.now().timestamp())
        exp = int(decodeJTW['exp'])
        user = decodeJTW['UserName']
        if exp > now and user and user != 'none':
            ret = True
        elif exp <= now and user and user != 'none':
            ret = False
    except:
        ret = False
        user = None

    return ret,user


def get_object_user(request,UserName):
    user = None
    try:
        UserName = str(UserName).replace("EIT\\", "")
        UserName = UserName + "@eit" if "@eit" not in UserName else UserName
        if Users.objects.filter(UserName=UserName).exists():
            user = create_not_exists_user(UserName)
    except:
        user = None
    return user
