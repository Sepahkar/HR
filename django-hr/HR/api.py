import json

from rest_framework.views import APIView
from rest_framework.response import Response
from HR.models import (
    Users,
    UserTeamRole,
    Role,
    Team,
)
from HR.serializers import (
    UsersSerializer,
    UserTeamRoleSerializer,
    AppUserAccessSerializer,
    PermissionUserSerializer,
    PermissionGroupSerializer,
    AllTeamServiceSerializer,
)
from rest_framework import status
from HR.decorators import private_api,public_api
from django.utils.decorators import method_decorator


class AllUsers(APIView):

    def get(self, request, *args, **kwargs):
        qs = Users.objects.all()
        user_serializer = UsersSerializer(qs,many=True)
        if user_serializer:
            return Response({'data':user_serializer.data},status=status.HTTP_200_OK)

        return Response(data={'state':'error'},status=status.HTTP_400_BAD_REQUEST)


class GetUser(APIView):
    def get(self,request, *args, **kwargs):
        qs = Users.objects.filter(UserName=kwargs.get('username')).first()
        if qs:
            user_serializer = UsersSerializer(qs)
            return Response({'data':user_serializer.data},status=status.HTTP_200_OK)

        return Response(data={'state':'error'},status=status.HTTP_400_BAD_REQUEST)


class GetUserTeamRole(APIView):

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username')
        qs = UserTeamRole.objects.filter(UserName__UserName=username)
        if qs:
            user_team_role_serializer = UserTeamRoleSerializer(qs,many=True)
            return Response({'data':user_team_role_serializer.data},status=status.HTTP_200_OK)

        return Response({'state':'error'}, status=status.HTTP_400_BAD_REQUEST)


class GetUserTeamRoles(APIView):

    def get(self, request, *args, **kwargs):
        wich_users = request.data.get('wich_users', 'active')
        if wich_users == 'active':
            qs = UserTeamRole.objects.filter(EndDate__isnull=True)
        elif wich_users == 'all':
            qs = UserTeamRole.objects.all()
        user_team_role_serializer = UserTeamRoleSerializer(qs,many=True)
        return Response({'data':user_team_role_serializer.data},status=status.HTTP_200_OK)

        return Response({'state':'error'}, status=status.HTTP_400_BAD_REQUEST)


class GetUserRoles(APIView):

    def get(self, request, *args, **kwargs):
        username = kwargs.get('username')
        qs = UserTeamRole.objects.filter(UserName_id=username)
        if qs:
            return Response({'data':list(qs.values_list("RoleId_id",flat=True))},status=status.HTTP_200_OK)

        return Response({'state':'error'}, status=status.HTTP_400_BAD_REQUEST)


class ExistsUsers(APIView):
    def get(self,request,*args,**kwargs):
        pk = kwargs.get('pk')
        ex = False
        if Users.objects.filter(pk=pk).exists():
            ex = True

        return Response({'data': ex}, status=200)


class ExistsRole(APIView):
    def get(self,request,*args,**kwargs):
        pk = kwargs.get('pk')
        ex = False
        if Role.objects.filter(pk=pk).exists():
            ex = True

        return Response({'data':ex},status=200)


class AllTeamService(APIView):
    def get(self, request, *args, **kwargs):
        qs = Team.objects.filter(ActiveInService=True)
        team_serializer = AllTeamServiceSerializer(qs,many=True)
        if team_serializer:
            return Response({'data':team_serializer.data},status=status.HTTP_200_OK)

        return Response(data={'state':'error'},status=status.HTTP_400_BAD_REQUEST)
