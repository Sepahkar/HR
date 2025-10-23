from functools import wraps


def private_api(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        function.is_private_api = True
        return function(request, *args, **kwargs)
    wrap.is_private_api = True
    return wrap


def public_api(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        return function(request, *args, **kwargs)
    wrap.is_public_api = True
    return wrap


def public_view(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        return function(request, *args, **kwargs)
    wrap.is_public_view = True
    return wrap


def hr_login_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        return function(request, *args, **kwargs)
    wrap.hr_login_required = True
    return wrap


def is_login_view(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        return function(request, *args, **kwargs)
    wrap.is_login_view = True
    return wrap


