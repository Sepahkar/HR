from django.urls import path
from HR.views_error import (
error_handle
)

app_name = "HR"
urlpatterns = [
    path('<str:error_name>/', error_handle, name="error_handle")
]