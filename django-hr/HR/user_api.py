from rest_framework.views import APIView
from rest_framework.response import Response
from HR.serializers import (
    AppUserAccessSerializer,
    PermissionUserSerializer,
    PermissionGroupSerializer,
    GroupSerializer,
    UsersSerializer,

)
from rest_framework import status
from django.contrib.auth.models import User,Group,Permission
from HR.jwt import check_is_admin


class AppUserAccess(APIView):

    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        is_admin = check_is_admin(token)
        if is_admin:
            username = kwargs.get('username')
            qs = User.objects.filter(username=username).first()
            if qs:
                current_serializer = AppUserAccessSerializer(qs)
                return Response({'data':current_serializer.data},status=status.HTTP_200_OK)
        return Response({'state':"error"}, status=status.HTTP_400_BAD_REQUEST)


class AppUserAppGroups(APIView):
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        is_admin = check_is_admin(token)
        if is_admin:
            qs = Group.objects.all()
            if qs:
                current_serializer = GroupSerializer(qs,many=True)
                return Response({'data':current_serializer.data},status=status.HTTP_200_OK)
        return Response({'state':"error"}, status=status.HTTP_400_BAD_REQUEST)


class AppUserUsersGroup(APIView):
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        is_admin = check_is_admin(token)
        if is_admin:
            group = kwargs.get('group')
            qs = User.objects.filter(groups__name=group)
            if qs:
                current_serializer = UsersSerializer(qs,many=True)
                return Response({'data':current_serializer.data},status=status.HTTP_200_OK)
        return Response({'state':"error"}, status=status.HTTP_400_BAD_REQUEST)


class AppUserGetUserPerms(APIView):
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        is_admin = check_is_admin(token)
        if is_admin:
            username = kwargs.get('username')
            qs = User.objects.filter(username=username).first()
            if qs:
                qs = qs.user_permissions
                current_serializer = PermissionUserSerializer(qs, many=True)
                return Response({'data':current_serializer.data}, status=status.HTTP_200_OK)
        return Response({'state':"error"}, status=status.HTTP_400_BAD_REQUEST)


class AppUserGetGroupPerms(APIView):
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        is_admin = check_is_admin(token)
        if is_admin:
            group = kwargs.get('group')
            qs = Group.objects.filter(name=group).first()
            if qs:
                qs = qs.permissions
                current_serializer = PermissionGroupSerializer(qs, many=True)
                return Response({'data':current_serializer.data}, status=status.HTTP_200_OK)

        return Response({'state':"error"}, status=status.HTTP_400_BAD_REQUEST)


class AppUserSetAccess(APIView):
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        is_admin = check_is_admin(token)
        if is_admin:
            username = kwargs.get('username')
            user = User.objects.filter(username=username).first()
            if user:
                user.is_active = int(request.POST.get('is_active'))
                user.is_staff = int(request.POST.get('is_staff'))
                user.is_superuser = int(request.POST.get('is_superuser'))
                user.save()
                return Response({'data':{'state':'ok'}},status=status.HTTP_200_OK)

        return Response({'data':{'state':"error"}}, status=status.HTTP_400_BAD_REQUEST)


class AppUserSetUserPerms(APIView):
    def post(self, request, *args, **kwargs):
        token = request.POST.get('token')
        is_admin = check_is_admin(token)
        if is_admin:
            username = kwargs.get('username')
            perms = request.POST.getlist('perms')
            user = User.objects.filter(username=username).first()
            if user:
                user.user_permissions.clear()
                for item in perms:
                    user.user_permissions.add(Permission.objects.get(id=item))
                return Response({'state': 'ok'}, status=status.HTTP_200_OK)

        return Response({'state':"error"}, status=status.HTTP_400_BAD_REQUEST)


class AppUserSetGroupPerms(APIView):
    def post(self, request, *args, **kwargs):
        pass


class AppUserCreateGroup(APIView):
    def post(self, request, *args, **kwargs):
        pass


class AppUserEditGroup(APIView):
    def post(self, request, *args, **kwargs):
        pass


class AppUserDeleteGroup(APIView):
    def post(self, request, *args, **kwargs):
        pass



