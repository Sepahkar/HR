from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Manager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, UserName, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not UserName:
            raise ValueError('The UserName must be set')
        email = self.normalize_email(UserName)
        user = self.model(UserName=UserName, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, UserName, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(UserName, password, **extra_fields)

