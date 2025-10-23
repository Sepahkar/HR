from django.urls import path
import HR.views as v
from HR.api import (
    AllUsers,
    GetUser,
    GetUserTeamRole,
    GetUserRoles,
    ExistsUsers,
    ExistsRole,
    GetUserTeamRoles,
    AllTeamService,
)
from HR.backends import show_404,show_403

app_name = "HR"
urlpatterns = [
    path('api/all-users/', AllUsers.as_view(), name="all_users" ),
    path('api/all-team-service/', AllTeamService.as_view(), name="all-team-service" ),
    path('api/get-user/<str:username>/', GetUser.as_view(), name="get_user" ),
    path('api/get-user-team-role/<str:username>/', GetUserTeamRole.as_view(), name="get_user_team_role" ),
    path('api/get-user-team-roles/', GetUserTeamRoles.as_view(), name="get_user_team_roles" ),
    path('api/get-user-roles/<str:username>/', GetUserRoles.as_view(), name="get_user_roles" ),

    #append from hr sh.mohammadhelmi@eit
    path('List/', v.UserPageList, name="hr_list"),
    path('<str:username>/', v.FirstPage, name="hr_firstpage"),
    path('contact/<str:username>/', v.ContactInfoPage, name="hr_contact"),
    path('', v.PersonInfoPage, name="hr_personeli"),
    path('person/<str:username>/', v.PersonInfoPage, name="hr_personeli"),
    path('job/<str:username>/', v.JobInfoPage, name="hr_job"),
    path('payment/<str:username>/', v.PaymentInfoPage, name="hr_payment"),
    path('worktime/<str:username>/', v.WorkTimeInfoPage, name="hr_worktime"),
    path('education/<str:username>/', v.EducationHistory, name="hr_personeli"),
    path('save/', v.UserSave),
    path('save/<str:action_type>', v.UserSave),
    path('detail/delete', v.UserDetailDelete),
    path('detail/save', v.UserDetailSave),

    # check exists api
    path('api/exists-users/<str:pk>/', ExistsUsers.as_view(), name="exists_users" ),
    path('api/exists-role/<str:pk>/', ExistsRole.as_view(), name="exists_role" ),


]