from django.apps import AppConfig


class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'HR'

    # def ready(self):
    #     from HR.utils import call_api
    #     from django.contrib.auth.models import User
    #
    #     @property
    #     def UserName(self):
    #         this_field = "UserName"
    #         request = get_request()
    #         username = self.username if "@eit" in self.username else self.username + "@eit"
    #         current_user = call_api(request, "HR", "get-user", username)
    #         return current_user.get(this_field)
    #
    #     @property
    #     def age(self):
    #         this_field = "age"
    #         request = get_request()
    #         username = self.username if "@eit" in self.username else self.username + "@eit"
    #         current_user = call_api(request, "HR", "get-user", username)
    #         return current_user.get(this_field)
    #
    #     @property
    #     def FullName(self):
    #         this_field = "FullName"
    #         request = get_request()
    #         username = self.username if "@eit" in self.username else self.username + "@eit"
    #         current_user = call_api(request, "HR", "get-user", username)
    #         return current_user.get(this_field)
    #
    #     @property
    #     def Gender(self):
    #         this_field = "Gender"
    #         request = get_request()
    #         username = self.username if "@eit" in self.username else self.username + "@eit"
    #         current_user = call_api(request, "HR", "get-user", username)
    #         return current_user.get(this_field)
    #
    #     @property
    #     def user_team_roles(self):
    #         request = get_request()
    #         username = self.username if "@eit" in self.username else self.username + "@eit"
    #         roles = call_api(request, "HR", "get-user-team-role", username)
    #         return roles
    #
    #     @property
    #     def permission_urls(self):
    #         request = get_request()
    #         username = self.username if "@eit" in self.username else self.username + "@eit"
    #         user_permission_urls = UserPermissionUrls(request,username)
    #         user_permission_urls.check_exists_permission_urls()
    #         return user_permission_urls.user_info
    #
    #     User.add_to_class("UserName", UserName)
    #     User.add_to_class("age", age)
    #     User.add_to_class("FullName", FullName)
    #     User.add_to_class("Gender", Gender)
    #     User.add_to_class("user_team_roles", user_team_roles)
    #     User.add_to_class('permission_urls',permission_urls)
        #from HR.jwt import init_tokens
        #print(init_tokens('a.jahani@eit'))
