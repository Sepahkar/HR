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
    GetAllRoles,
    GetAllTeams,
    GetViewRoleTarget,
    GetViewRoleTeam,
    CallSpAssessorsEducator,
    CallSpGetTeamsOfRole,
    CallSpGetManagerOfTeam,
    CallSpGetTargetRole,
    CallFuncEducatorGetTeamManager,
    AllTeamEvaluation,
    FindTeam,
    GetPreviousUserTeamRoles,
    GetAllViewRoleTeam,
)
from HR.backends import show_404,show_403

app_name = "HR"
urlpatterns = [
    path('api/all-users/', AllUsers.as_view(), name="all_users" ),
    path('api/all-team-service/', AllTeamService.as_view(), name="all-team-service" ),
    path('api/all-team-evaluation/', AllTeamEvaluation.as_view(), name="all-team-evaluation"),
    path('api/find-team/', FindTeam.as_view(), name="find-team"),
    path('api/get-user/<str:username>/', GetUser.as_view(), name="get_user" ),
    path('api/get-user-team-role/<str:username>/', GetUserTeamRole.as_view(), name="get_user_team_role" ),
    path('api/get-user-team-roles/', GetUserTeamRoles.as_view(), name="get_user_team_roles" ),
    path('api/get-user-roles/<str:username>/', GetUserRoles.as_view(), name="get_user_roles" ),
    path('api/get-all-roles/', GetAllRoles.as_view(), name="get_all_roles" ),
    path('api/get-all-teams/', GetAllTeams.as_view(), name="get_all_teams" ),
    path('api/get-v-role-target/', GetViewRoleTarget.as_view(), name="get_v_role_target"),
    path('api/get-v-role-team/', GetViewRoleTeam.as_view(), name="get_v_role_team"),
    path('api/get-previous-user-team-roles/', GetPreviousUserTeamRoles.as_view(), name="get_previous_user_team_roles"),
    path('api/get-all-v-role-team/', GetAllViewRoleTeam.as_view(), name="get_all_v_role_team"),

    # this urls for sp sql
    path('api/call-sp-assessors-educator/', CallSpAssessorsEducator.as_view(), name="call_sp_assessors_educator"),
    path('api/call-sp-get-teams-of-role/', CallSpGetTeamsOfRole.as_view(), name="call_sp_get_teams_of_role"),
    path('api/call-sp-get-manager-of-team/', CallSpGetManagerOfTeam.as_view(), name="call_sp_get_manager_of_team"),
    path('api/call-sp-get-target-role/', CallSpGetTargetRole.as_view(), name="call_sp_get_target_role"),
    path('api/call-func-educator-get-team-manager/', CallFuncEducatorGetTeamManager.as_view(), name="call_func_educator_get_team_manager"),

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
    path('facilities/<str:username>/', v.FacilitiesInfoPage, name="hr_personeli"),
    path('save/', v.UserSave),
    path('save/<str:action_type>', v.UserSave),
    path('detail/delete', v.UserDetailDelete),
    path('detail/save', v.UserDetailSave),
    path('saveimageuser/', v.SaveImageUser ,name='save_image_user'),

    # check exists api
    path('api/exists-users/<str:pk>/', ExistsUsers.as_view(), name="exists_users" ),
    path('api/exists-role/<str:pk>/', ExistsRole.as_view(), name="exists_role" ),


]