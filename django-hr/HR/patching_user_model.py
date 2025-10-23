from django.contrib.auth.models import User
from django_middleware_global_request.middleware import get_request
from HR.utils import call_api


current_user = {}


@property
def UserName(self):
    global current_user
    this_field = "UserName"
    if this_field not in current_user:
        request = get_request()
        username = self.username if "@eit" in self.username else self.username + "@eit"
        current_user = call_api(request, "HR", "get-user", username)
        return current_user.get(this_field)
    elif this_field in current_user:
        return current_user.get(this_field)


User.add_to_class("UserName",UserName)