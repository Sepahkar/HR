from django_user_agents.utils import get_user_agent
import re
from django.http.response import HttpResponse, HttpResponseRedirect
from HR.utils import get_super_superusers, get_all_apps, call_api_custom_url
from HR.jwt import decrypt, init_tokens, encrypt, enc_jwt, dec_jwt, validate_access_token_and_auth_user, \
    create_cookie_on_response
import time
from django.template.loader import render_to_string
from django.utils.deprecation import MiddlewareMixin
from django.http.response import JsonResponse
from dotenv import load_dotenv
from pathlib import Path
import os
from django.utils.functional import SimpleLazyObject
from django.contrib import auth
from django.conf import settings

dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=os.path.join(dir, ".env"))


# request.user = SimpleLazyObject(lambda: get_user(request))
def get_user(request):
    if not hasattr(request, '_cached_user'):
        request._cached_user = auth.get_user(request)
    return request._cached_user


class DetectUserInfoMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        """
        One-time configuration and initialisation.
        """
        super().__init__(get_response)

    def process_request(self, request):

        if "/api/" in request.path:
            return None

        user_agent = get_user_agent(request)
        not_support_browser = True
        for item in os.getenv('ACCESS_BROWSERS').split(','):
            if re.search(item, user_agent.browser.family, re.IGNORECASE):
                not_support_browser = False
                break

        if not_support_browser:
            response = HttpResponse()
            response.status_code = "custom_not_support_browser"
            return response

        first_path_word = request.path.split('/')[1]
        if first_path_word in ["error", "admin"]:
            return None

        if "show_login_page" in request.GET and str(request.GET.get('show_login_page')) == '1':
            setattr(self.get_response, 'show_login_page', '1')
            return None

        if "force_login" in request.GET and str(request.GET.get('force_login')) == '1':
            url = self.get_redirect_login_url(request)
            response = HttpResponseRedirect(redirect_to=url)
            return response

        if "access" in request.GET:
            valid_token, auth_user, new_access = validate_access_token_and_auth_user(request, request.GET.get("access"))
            if valid_token and auth_user and new_access:
                setattr(self.get_response, 'access', new_access)
                return None
            else:
                return HttpResponseRedirect(redirect_to=self.get_negotiate_url(request))

        return None

    def process_view(self, request, view_func, *view_args, **view_kwargs):

        if "/api/" in request.path:
            # this section check class base view api e.g APIView
            if hasattr(view_func,'view_class'):
                method_names = [item for item in view_func.view_class.__dict__.keys() if not str(item).startswith("_")]
                is_private = False
                is_public = False
                for item in method_names:
                    if hasattr(view_func.view_class,item):
                        cur_view = getattr(view_func.view_class,item)
                        if hasattr(cur_view,'is_private_api'):
                            is_private = True
                        if hasattr(cur_view, 'is_public_api'):
                            is_public = True

                if is_private:
                    if self.check_api_access(request):
                        return None
                    return JsonResponse(data={'message': 'permission denied'}, status=403)

                if is_public:
                    return None
            # end

            # this section check function base view api
            if hasattr(view_func, 'is_public_api'):
                return None
            if hasattr(view_func, 'is_private_api'):
                if self.check_api_access(request):
                    return None
                return JsonResponse(data={'message': 'permission denied'}, status=403)
            #end

            # default api return None that means by default all api is public
            return None

        first_path_word = request.path.split('/')[1]
        if first_path_word in ["admin"]:
            access = request.COOKIES.get('access') if "access" not in request.GET else request.GET.get('access')
            valid_token, auth_user, new_access = validate_access_token_and_auth_user(request, access)
            if valid_token and auth_user and new_access:
                response = self.get_and_detect_response_for_view_func(view_func, request, view_args, view_kwargs)
                response = create_cookie_on_response(request, response, access=new_access)
                return response
                return None
            return HttpResponseRedirect(redirect_to=self.get_negotiate_url(request))


        if first_path_word in ["error"]:
            return None

        # this section check class base view is public or not
        is_public_checked_in_step_class_base_view = False
        if hasattr(view_func,'view_class'):
            method_names = [item for item in view_func.view_class.__dict__.keys() if not str(item).startswith("_")]
            is_public = False
            for item in method_names:
                if hasattr(view_func.view_class, item):
                    cur_view = getattr(view_func.view_class, item)
                    if hasattr(cur_view, 'is_public_view'):
                        is_public = True
                    if hasattr(cur_view, 'hr_login_required'):
                        is_public_checked_in_step_class_base_view = True
            if is_public:
                return None
        #end

        if hasattr(view_func, 'is_public_view') or '/AccessControl/CheckUserPermission' in request.path or '/AccessControl/GetAppTeams' in request.path or '/AccessControl/GetUserURLs' in request.path or '/AccessControl/GetUserPermissions' in request.path:
            return None

        if hasattr(self.get_response, 'show_login_page'):
            if hasattr(view_func, 'is_login_view'):
                return None

        if hasattr(self.get_response, 'access'):
            access = getattr(self.get_response, 'access')
            delattr(self.get_response, 'access')
        else:
            access = request.COOKIES.get('access')
        valid_token, auth_user, new_access = validate_access_token_and_auth_user(request, access)
        if valid_token and auth_user and new_access:
            request.user = SimpleLazyObject(lambda: get_user(request))
            if hasattr(view_func, 'hr_login_required') or is_public_checked_in_step_class_base_view:
                # try:
                #     response = view_func(request, view_args, view_kwargs)
                # except:
                #     response = view_func(request)
                response = self.get_and_detect_response_for_view_func(view_func, request, view_args, view_kwargs)
                response = create_cookie_on_response(request, response, access=new_access)
                return response
            has_permission = self.check_access_current_url(request)
            if has_permission:
                # try:
                #     response = view_func(request, view_args, view_kwargs)
                # except:
                #     response = view_func(request)
                response = self.get_and_detect_response_for_view_func(view_func,request, view_args, view_kwargs)
                response = create_cookie_on_response(request, response, access=new_access)
                return response
            else:
                response = HttpResponse()
                response.status_code = "403"
                return response
        else:
            return HttpResponseRedirect(redirect_to=self.get_negotiate_url(request))



        return None

    def process_response(self, request, response):
        if settings.DEBUG and str(response.status_code) == "500": return response

        if "custom" in str(response.status_code):
            status_code = str(response.status_code).split("custom_")[1]
            if settings.DEBUG and str(status_code) == "500": return response

            if status_code == "redirect":
                response = HttpResponseRedirect(response.redirect_url)
            else:
                rendered = render_to_string(f'HR/{status_code}.html')
                response = HttpResponse(rendered)

        elif str(response.status_code) in ["404", "500"]:
            status_code = response.status_code
            rendered = render_to_string(f'HR/{status_code}.html')
            response = HttpResponse(rendered)

        return response

    def get_redirect_login_url(self, request):
        schema = "https://" if request.is_secure() else "http://"
        current_full_path = schema + request.get_host() + request.get_full_path()
        data = get_all_apps(request, return_dict=1)
        from_ip = request.get_host().split(":")[0]
        from_port = request.get_host().split(":")[1]
        if "?access" in current_full_path:
            current_full_path = current_full_path.split("?access")[0]
        if "&access" in current_full_path:
            current_full_path = current_full_path.split("&access")[0]
        redirect_url = data.get("Portal").get('APPSCHEMA') +  str(data.get("Portal").get('APPIP')) + ':' + str(data.get("Portal").get('APPPORT')) + "/AuthUser/Login/" + f"?from_ip={from_ip}&from_port={from_port}&show_login_page=1"
        if "next" in request.GET:
            redirect_url += "&next="+request.GET.get("next")
        return redirect_url


    def get_negotiate_url(self, request):
        schema = "https://" if request.is_secure() else "http://"
        current_full_path = schema + request.get_host() + request.get_full_path()
        if str(request.path).startswith("/admin/") and "/admin/" in current_full_path:
            current_full_path = current_full_path.split("/admin")[0] + "/admin/"
        from_ip = request.get_host().split(":")[0]
        from_port = request.get_host().split(":")[1]
        if "?access" in current_full_path:
            current_full_path = current_full_path.split("?access")[0]
        if "&access" in current_full_path:
            current_full_path = current_full_path.split("&access")[0]
        redirect_url = schema + f"eit-app:24000/?detect=1&from_ip={from_ip}&from_port={from_port}&next={current_full_path}"
        if "force_login" in request.GET:
            data = get_all_apps(request, return_dict=1)
            redirect_url = str(data.get('Portal').get('FullUrl')) + '/AuthUser/Login/'

        return redirect_url

    def get_current_auth_middleware_url(self, request, access):
        schema = "https://" if request.is_secure() else "http://"
        current_full_path = schema + request.get_host() + request.get_full_path()
        redirect_url = schema + f"{current_full_path}&auth_middleware={access}"
        if "next" in request.GET:
            redirect_url += "&next=" + request.GET.get('next')
        if "force_login" in request.GET:
            data = get_all_apps(request, return_dict=1)
            redirect_url = str(data.get('Portal').get('FullUrl')) + '/AuthUser/Login/'

        return redirect_url

    def check_api_access(self, request):
        if self.is_valid_auth_token(request):
            return True
        return False

    def check_access_current_url(self, request):
        # schema = "https://" if request.is_secure() else "http://"
        # cur_full_path = schema + request.get_host() + request.get_full_path()
        # permission_urls = request.user.permission_urls
        #
        # is_public_url = False
        # if is_public_url:
        #     return True
        return True

    def is_valid_auth_token(self, request):
        ret = False
        auth_token = None
        try:
            if request.META.get('HTTP_AUTHORIZATION') and "Bearer " in request.META.get('HTTP_AUTHORIZATION'):
                auth_token = request.META.get('HTTP_AUTHORIZATION').split("Bearer ")[1]
            data = dec_jwt(auth_token)
            if "time" in data:
                now = int(round(time.time() * 1000))
                diff = int((now - int(data.get('time'))) / 1000)
                if diff <= 60:
                    ret = True
        except:
            ret = False

        return ret

    def get_and_detect_response_for_view_func(self,view_func,request, view_args, view_kwargs):
        try:
            flg_view_args = True if len(view_args) > 1 and view_args[1] else False
        except:
            flg_view_args = False
        # try:
        #     flg_view_kwargs = True if view_kwargs else False
        # except:
        #     flg_view_kwargs = False
        # if flg_view_args and flg_view_kwargs:
        #     view_args = tuple(view_args[1].values())
        #     return view_func(request,*view_args, **view_kwargs)
        # elif flg_view_args and not flg_view_kwargs:
        #     view_args = tuple(view_args[1].values())
        #     return view_func(request, *view_args)
        # elif not flg_view_args and flg_view_kwargs:
        #     return view_func(request, **view_kwargs)
        # else:
        #     return view_func(request)
        if flg_view_args:
            _view_kwargs = view_args[1]
            view_kwargs.update(_view_kwargs)
            return view_func(request, **view_kwargs)
        else:
            return view_func(request)