import time
import traceback
import requests
from django.conf import settings
import json
import os
from HR.jwt import enc_jwt
from django_middleware_global_request.middleware import get_request
from dotenv import load_dotenv
from pathlib import Path
dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=os.path.join(dir,".env"))


def get_url_apps_info_in_access_control(return_dict):
    try:
        url = settings.ACCESSCONTROL_IP_PORT + "/AccessControl/api/get-all-apps-info/"
        if return_dict:
            url += "?return-dict=1"
    except:
        url = "http://192.168.20.81:13000/AccessControl/api/get-all-apps-info/"
        if return_dict:
            url += "?return-dict=1"
    return url


def get_obj_with_key(_key, _val, _list):
    ret = {}
    for item in _list:
        if _key in item:
            val = item.get(_key).lower()
            if val == _val.lower():
                ret = item
                break
    return ret


def generate_auth_token(request):
    now = str(int(round(time.time() * 1000)))
    from_ip = str(request.get_host()).split(":")[0]
    from_port = str(request.get_host()).split(":")[1]
    data = {'time':now,'from_ip':from_ip,'from_port':from_port}
    data = enc_jwt(data)
    return str(data)


def get_all_apps(request=None,return_dict=None,data=None,headers=None):
    if request is None:
        request = get_request()
    _headers = {'Content-Type':'application/json','Authorization':f'Bearer {generate_auth_token(request)}'}
    url = get_url_apps_info_in_access_control(return_dict)
    try:
        if data and type(data) is dict:
            data = json.dumps(data)
        res_all_app_info = requests.get(url,params=data,headers=_headers)
        if res_all_app_info.status_code == 200:
            all_app_info = res_all_app_info.json().get('data')
            if all_app_info:
                return all_app_info
    except:
        traceback.print_exc()


def generate_link(request, app_name, api_name, variables=None, has_get_parameter=None):
    all_app_info = get_all_apps(request)
    app_info = get_obj_with_key('AppName', app_name, all_app_info)
    url = app_info.get('APPSCHEMA') + str(app_info.get('APPIP')) + ":" + str(app_info.get('APPPORT')) + f"/{app_name}/api/{api_name}"
    if variables:
        url += "/" + str(variables) + "/"
    else:
        url += "/"
    return url


def generate_link_custom_url(request, app_name, api_url, variables=None,has_get_parameter=None):
    all_app_info = get_all_apps(request)
    app_info = get_obj_with_key('AppName', app_name, all_app_info)
    url = app_info.get('APPSCHEMA') + str(app_info.get('APPIP')) + ":" + str(app_info.get('APPPORT')) + f"/{api_url}"
    if variables:
        url += "/" + str(variables) + "/"
    else:
        url += "/"
    return url


def call_api(request, app_name, api_name, variables=None,has_get_parameter=None,data=None,headers=None):
    url = generate_link(request, app_name, api_name, variables,has_get_parameter)
    _headers = {'Content-Type':'application/json','Authorization':f'Bearer {generate_auth_token(request)}'}
    if data and type(data) is dict:
        data = json.dumps(data)
    res = requests.get(url,params=data,headers=_headers)
    if res.status_code == 200:
        return res.json().get('data')


def call_api_post(request, app_name, api_name, variables=None, data=None,headers=None,has_get_parameter=None):
    _headers = {'Content-Type':'application/json','Authorization':f'Bearer {generate_auth_token(request)}'}
    url = generate_link(request, app_name, api_name, variables,has_get_parameter)
    if data and type(data) is dict:
        data = json.dumps(data)
    res = requests.post(url, data=data, headers=_headers)
    if res.status_code == 200:
        return res.json().get('data')


def call_api_custom_url(request, app_name, api_url, variables=None,data=None, headers=None,has_get_parameter=None):
    url = generate_link_custom_url(request, app_name, api_url, variables,has_get_parameter)
    _headers = {'Content-Type':'application/json','Authorization':f'Bearer {generate_auth_token(request)}'}
    if data and type(data) is dict:
        data = json.dumps(data)
    if headers:
        _headers.update(headers)
    res = requests.get(url, params=data, headers=_headers)
    if res.status_code == 200:
        return res.json().get('data')


def call_api_post_custom_url(request, app_name, api_url, variables=None, data=None, headers=None,has_get_parameter=None):
    url = generate_link_custom_url(request, app_name, api_url, variables,has_get_parameter)
    _headers = {'Content-Type':'application/json','Authorization':f'Bearer {generate_auth_token(request)}'}
    if data and type(data) is dict:
        data = json.dumps(data)
    res = requests.post(url, data=data, headers=_headers)
    if res.status_code == 200:
        return res.json().get('data')


def call_api_put_custom_url(request, app_name, api_url, variables=None, data=None, headers=None,has_get_parameter=None):
    url = generate_link_custom_url(request, app_name, api_url, variables,has_get_parameter)
    _headers = {'Content-Type':'application/json','Authorization':f'Bearer {generate_auth_token(request)}'}
    if data and type(data) is dict:
        data = json.dumps(data)
    res = requests.put(url, data=data, headers=_headers)
    if res.status_code == 200:
        return res.json().get('data')


def get_app_info(request, app_name, api_name, variables=None):
    data = call_api(request, app_name, api_name, variables)
    ret = None
    if data:
        for item in data:
            if item.get('AppName') == app_name:
                ret = item
                break
    return ret


def get_super_superusers():
    return os.getenv('LIST_SUPER_SUPERUSERS').split(',')


# class UserPermissionUrls:
#
#     def __init__(self,request,username):
#         self.is_connected = True
#         self.redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
#         try:
#             self.redis_instance.get('justfortestconnection')
#         except:
#             self.is_connected = False
#             print("Redis Server Is Not Running...")
#         self.user_info = {}
#         self.request = request
#         self.username = username
#         self.username_no_eit = self.username.replace("@eit", "")
#
#     def get_data(self,key):
#         data = None
#         if self.is_connected:
#             try:
#                 data = self.redis_instance.get(key)
#                 data = self.byte_to_dict(data) if data else None
#             except:
#                 print(f"not found data with key {key}")
#
#         return data
#
#     def update_user_info(self,**kwargs):
#         if self.is_connected:
#             data = self.get_data(self.username_no_eit)
#             if data is not None:
#                 self.user_info = data.get('permission_urls') if "permission_urls" not in kwargs else kwargs.get('permission_urls')
#
#     def set_data(self,user_info):
#         if self.is_connected:
#             self.redis_instance.set(self.username_no_eit, self.dict_to_byte(user_info))
#
#     def get_new_permission_urls(self):
#         if self.is_connected:
#             data = call_api_custom_url(self.request, "AccessControl", "AccessControl/api/get-user-all-urls",
#                                        variables=self.username)
#             user_info = {
#                 'permission_urls': data.get('rows')
#             }
#             self.set_data(user_info)
#
#     def check_exists_permission_urls(self):
#         if self.is_connected:
#             if self.request.user.is_authenticated:
#                 try:
#                     user_info = self.get_data(self.username_no_eit)
#                     if user_info:
#                         if "permission_urls" in user_info:
#                             self.update_user_info(**user_info)
#                         elif "permission_urls" not in user_info:
#                             self.get_new_permission_urls()
#                             self.update_user_info()
#                     else:
#                         self.get_new_permission_urls()
#                         self.update_user_info()
#                 except:
#                     traceback.print_exc()
#                     print("errror at get user permissions")
#
#     def delete_exists_permission_urls(self):
#         if self.is_connected:
#             user_info = self.get_data(self.username_no_eit)
#             if user_info and "permission_urls" in user_info:
#                 del user_info['permission_urls']
#                 self.set_data(user_info)
#
#
#     def byte_to_dict(self,_byte):
#         if self.is_connected:
#             if _byte:
#                 return json.loads(_byte.decode('utf-8'))
#             return {}
#
#     def dict_to_byte(self,_dict):
#         if self.is_connected:
#             if _dict:
#                 return json.dumps(_dict, indent=2).encode('utf-8')
#             return b''