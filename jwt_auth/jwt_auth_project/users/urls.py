from django.urls import path
from . import views
from . import views
from .otp_views import request_otp, verify_otp


urlpatterns = [
    path("register", views.register),
    path("login/", views.login),
    path("user/refresh", views.refresh_access),
    path("protected", views.protected),
    
    path("otp/request/", request_otp),
    path("otp/verify/", verify_otp),
    

]
