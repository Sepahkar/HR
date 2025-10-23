import json

from rest_framework import serializers
from HR.models import (
    Users,
    UserTeamRole,
    Team,
)
from django.contrib.auth.models import User,Permission,Group


class UsersSerializer(serializers.ModelSerializer):
    UserName = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    FullName = serializers.SerializerMethodField()
    degree = serializers.SerializerMethodField()
    contract = serializers.SerializerMethodField()
    user_image_name = serializers.SerializerMethodField()
    Gender = serializers.SerializerMethodField()
    GenderTitle = serializers.SerializerMethodField()
    GenderTitlePrefix = serializers.SerializerMethodField()
    GenderTitlePrefixFullName = serializers.SerializerMethodField()
    Email = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ('UserName','age','FullName','degree','contract','user_image_name','Gender','GenderTitle','GenderTitlePrefix','GenderTitlePrefixFullName','Email')

    def get_UserName(self,obj):
        return obj.UserName

    def get_age(self,obj):
        return obj.get_birth

    def get_FullName(self,obj):
        return obj.FullName

    def get_degree(self,obj):
        return obj.get_degree

    def get_contract(self,obj):
        return obj.get_contract

    def get_user_image_name(self,obj):
        return obj.user_image_name

    def get_Gender(self,obj):
        return obj.Gender

    def GenderTitle(self, obj):
        return obj.GenderTitle

    def GenderTitlePrefix(self, obj):
        return obj.GenderTitlePrefix

    def GenderTitlePrefixFullName(self, obj):
        return obj.GenderTitlePrefixFullName

    def get_Email(self, obj):
        return (obj.UserName.replace("@eit","")) + "@iraneit.com"



class UserTeamRoleSerializer(serializers.ModelSerializer):
    FullName = serializers.CharField(source="UserName.FullName")
    TeamName = serializers.CharField(source="TeamCode.TeamName")
    class Meta:
        model = UserTeamRole
        fields = '__all__'


class AppUserAccessSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'is_active',
            'is_staff',
            'is_superuser',
        )


class PermissionUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class PermissionGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionUserSerializer(many=True,read_only=True)
    class Meta:
        model = Group
        fields = (
            'id',
            'name',
            'permissions',
        )



class AllTeamServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = '__all__'