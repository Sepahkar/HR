from django.urls import path
from HR.user_api import (
    AppUserAccess,
    AppUserGetUserPerms,
    AppUserGetGroupPerms,
    AppUserSetAccess,
    AppUserSetUserPerms,
    AppUserSetGroupPerms,
    AppUserCreateGroup,
    AppUserEditGroup,
    AppUserDeleteGroup,
    AppUserAppGroups,
    AppUserUsersGroup,
)
from HR.views import (
    get_internal_token,
)


urlpatterns = [
    path('access/<str:username>/', AppUserAccess.as_view(), name="app_user_get_user_access"),
    path('app-groups/', AppUserAppGroups.as_view(), name="app_user_get_app_groups"),
    path('users-group/<str:group>/', AppUserUsersGroup.as_view(), name="app_user_get_users_group"),

    path('user-perms/<str:username>/', AppUserGetUserPerms.as_view(), name="app_user_get_user_perms"),
    path('group-perms/<str:group>/', AppUserGetGroupPerms.as_view(), name="app_user_get_group_perms"),

    path('set-access/<str:username>/', AppUserSetAccess.as_view(), name="app_user_set_user_access"),
    path('set-user-perms/<str:username>/', AppUserSetUserPerms.as_view(), name="app_user_set_user_perms"),
    path('set-group-perms/<str:group>/', AppUserSetGroupPerms.as_view(), name="app_user_set_group_perms"),

    path('create-group/<str:group>/', AppUserCreateGroup.as_view(), name="app_user_create_group"),
    path('edit-group/<str:group>/', AppUserEditGroup.as_view(), name="app_user_edit_group"),
    path('delete-group/<str:group>/', AppUserDeleteGroup.as_view(), name="app_user_delete_group"),


    # call from internall every app
    path('get-internal-token/',get_internal_token,name="get_internal_token"),
]