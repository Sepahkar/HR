import datetime
from django.shortcuts import render
import pytz
from django.contrib.auth.backends import ModelBackend
import ldap
from django.conf import settings
from django.db import connections
from django.contrib.auth import login
from django.shortcuts import redirect
from django.http import HttpResponseRedirect,HttpResponse
from django_middleware_global_request.middleware import get_request

from HR.models import UserHistory,Users
from HR.decorators import public_view
from django.contrib.auth.models import User


class LdapBackend(ModelBackend):
    AUTHENTICATE_URL_PREFIX = 'http://eit-app:23000/'
    REDIRECT_LOGIN = AUTHENTICATE_URL_PREFIX + 'AuthUser/Login'
    def authenticate(self, request, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        username = username + "@eit" if "@eit" not in username else username
        try:
            ldap_host = settings.AUTH_LDAP_SERVER_URI
            ldap_con = ldap.initialize(ldap_host)
        except ldap.SERVER_DOWN:
            return HttpResponse("<h1>cant connect ldap server</h1>")

        try:
            ldap_con.set_option(ldap.OPT_REFERRALS, 0)
            ldap_con.simple_bind_s(username, password)
            user = create_not_exists_user(username)
            if user:
                return user
        except (ldap.INVALID_CREDENTIALS):
            pass

        return None

    def get_user(self, user_id):
        request = get_request()
        if "/admin/" in request.get_full_path():
            return User.objects.get(id=user_id)
        username = User.objects.get(id=user_id).username
        username = username+"@eit" if "@eit" not in username else username
        user = Users.objects.filter(UserName=username).first()
        return user

    # def get_all_permissions(self, user_obj, obj=None):
    #     user_id = get_user_id(user_obj.username)
    #     perms = []
    #     if user_id is not None:
    #         try:
    #             arr = get_permissions_user(user_id)
    #             int_perms = [item[2] for item in arr]
    #             str_perms = get_permissions_string(int_perms)
    #             perms1 = [str(item[4])+'.'+str(item[2]) for item in str_perms]
    #             perms2 = self.get_group_permissions(user_obj)
    #             perms3 = self.get_user_permissions(user_obj)
    #             perms = perms1 + perms2 + perms3
    #         except:
    #             perms = []
    #     return perms
    #
    # def get_user_permissions(self, user_obj, obj=None):
    #     return []
    #
    # def get_group_permissions(self, user_obj, obj=None):
    #     try:
    #         groups = get_groups_of_current_user(user_obj.username)
    #         int_perms = get_permissions_of_groups(groups)
    #         str_perms = get_permissions_string(int_perms)
    #         if str_perms:
    #             perms = [str(item[4]) + '.' + str(item[2]) for item in str_perms]
    #     except:
    #         perms = []
    #     return perms


def create_not_exists_user(username):
    username = username+"@eit" if "@eit" not in username else username
    email = username.replace("@eit", "@iraneit.com")
    date_joined = datetime.datetime.now().date()
    user = User.objects.filter(username=username).first()
    if user:
        return user
    user = User(
        username=username,
        password='0',
        email=email,
        date_joined=date_joined,
        is_active=1,
        is_staff=1,
        is_superuser=0,
        first_name=' ',
        last_name=' '
    )
    user.save()
    return user

def get_or_create(username,**kwargs):
    if kwargs.get('dbs') is not None:
        connections.databases['VIR'].update(kwargs.get('dbs'))
        cursor = connections['VIR'].cursor()
    else:
        cursor = connections['default'].cursor()
    try:
        cursor.execute("select * from auth_user where username=%s " , (username,))
        row = cursor.fetchone()
        if row is None:
            email = username.replace("@eit", "@iraneit.com")
            date_joined = datetime.datetime.now().date()
            cursor.execute("insert into auth_user (username,password,email,date_joined,is_active,is_staff,is_superuser,first_name,last_name) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(username,'0',email,date_joined,1,1,0,'',''))
    except:
        cursor.close()
    finally:
        cursor.close()


def get_user_id(username,**kwargs):
    if kwargs.get('dbs') is not None:
        connections.databases['VIR'].update(kwargs.get('dbs'))
        cursor = connections['VIR'].cursor()
    else:
        cursor = connections['default'].cursor()
    try:
        cursor.execute("select * from auth_user where username=%s " , (username,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
    except:
        cursor.close()
    finally:
        cursor.close()

    return None


def get_permissions_user(user_id):
    cursor = connections['default'].cursor()
    #cursor = connection.cursor()
    try:
        cursor.execute("select * from auth_user_user_permissions where user_id=%s " , (user_id,))
        row = cursor.fetchall()
        if row is not None:
            return row
    except:
        cursor.close()
    finally:
        cursor.close()

    return None


def get_permissions_string(list_ids,**kwargs):
    if kwargs.get('dbs') is not None:
        connections.databases['VIR'].update(kwargs.get('dbs'))
        cursor = connections['VIR'].cursor()
    else:
        cursor = connections['default'].cursor()
    list_ids = list(map(str,list_ids))
    ids = ",".join(list_ids)
    try:
        cursor.execute("select auth_permission.id,auth_permission.content_type_id,auth_permission.codename,django_content_type.id,django_content_type.app_label,django_content_type.model,auth_permission.name from auth_permission inner join django_content_type ON django_content_type.id=auth_permission.content_type_id where auth_permission.id IN("+ids+") ")
        row = cursor.fetchall()
        if row is not None:
            return row
    except:
        cursor.close()
    finally:
        cursor.close()

    return None


def update_permissions(user_id,perm_list,**kwargs):
    if kwargs.get('dbs') is not None:
        connections.databases['VIR'].update(kwargs.get('dbs'))
        cursor = connections['VIR'].cursor()
    else:
        cursor = connections['default'].cursor()
    ret = True

    try:
        cursor.execute("delete from auth_user_user_permissions where user_id=%s ", (user_id,))
        for perm_id in perm_list:
            try:
                cursor.execute("insert into auth_user_user_permissions (user_id,permission_id) values(%s,%s)", (user_id,perm_id))
            except:
                pass
    except:
        ret = False
        cursor.close()
    finally:
        cursor.close()

    return ret


def update_permissions_group(user_id,group_list,**kwargs):
    if kwargs.get('dbs') is not None:
        connections.databases['VIR'].update(kwargs.get('dbs'))
        cursor = connections['VIR'].cursor()
    else:
        cursor = connections['default'].cursor()
    ret = True
    try:
        cursor.execute("delete from auth_user_groups where user_id=%s ", (user_id,))
        for group_id in group_list:
            try:
                cursor.execute("insert into auth_user_groups (user_id,group_id) values(%s,%s)", (user_id,group_id))
            except:
                pass
    except:
        ret = False
        cursor.close()
    finally:
        cursor.close()

    return ret


def get_groups(**kwargs):
    if kwargs.get('dbs') is not None:
        connections.databases['VIR'].update(kwargs.get('dbs'))
        cursor = connections['VIR'].cursor()
    else:
        cursor = connections['default'].cursor()
    try:
        cursor.execute("select * from auth_group")
        row = cursor.fetchall()
        if row is not None:
            return row
    except:
        cursor.close()
    finally:
        cursor.close()

    return None


def get_groups_of_current_user(username):
    cursor = connections['default'].cursor()
    #cursor = connection.cursor()
    user_id = get_user_id(username)
    if user_id is not None:
        try:
            cursor.execute("select * from auth_user_groups where user_id=%s",(user_id,))
            row = cursor.fetchall()
            if row is not None:
                rows = [item[2] for item in row]
                return rows
        except:
            cursor.close()
        finally:
            cursor.close()

        return []


def get_permissions_of_groups(group_ids,**kwargs):
    if kwargs.get('dbs') is not None:
        connections.databases['VIR'].update(kwargs.get('dbs'))
        cursor = connections['VIR'].cursor()
    else:
        cursor = connections['default'].cursor()
    group_ids = list(map(str,group_ids))
    ids = ",".join(group_ids)
    try:
        cursor.execute("select permission_id from auth_group_permissions where group_id IN ("+ids+")")
        perms = cursor.fetchall()
        permission_ids = [item[0] for item in perms]
        permission_ids = list(map(str,permission_ids))
        return permission_ids
    except:
        cursor.close()
    finally:
        cursor.close()

    return None



@public_view
def check_auth_user(request):
    auth_key = request.GET.get('auth_key')
    url = request.GET.get('url')
    user = Users.objects.filter(AuthLoginKey__exact=auth_key).first()
    if user and user.AuthLoginDate:
        tz = pytz.timezone("Asia/Tehran")
        now = datetime.datetime.now(tz)
        diff = datetime.datetime.fromisoformat(str(now).split(".")[0]) - datetime.datetime.fromisoformat(str(user.AuthLoginDate).split(".")[0])
        diff = diff.total_seconds() / 60
        pattern = 1 # this line calc 3 hour 30 minute to minute and plus with 1 minute
        if diff <= pattern:
            user.AuthLoginKey = None
            user.AuthLoginDate = None
            user.save()
            ip = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT')
            user_history = UserHistory.objects.filter(AuthLoginKey__exact=auth_key).first()
            changed_user_info = True
            if user_history and user_history.IP == ip and user_history.UserAgent == user_agent:
                changed_user_info = False
            user_history.ChangedUserInfo = changed_user_info
            user_history.EnterUrl = url
            user_history.EnterDate = datetime.datetime.now(tz)
            user_history.save()
            if changed_user_info == False:
                user = create_not_exists_user(user.UserName)
                login(request, user)
                return redirect(url)
    return HttpResponseRedirect('/error/403/')



def show_403(request):
    return render(request,"HR/403.html")


def show_404(request):
    return render(request,"HR/404.html")


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


