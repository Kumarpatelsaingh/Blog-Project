from django.urls import path

from authentication.views import UserLogin, UserSignup, UserLogout

urlpatterns = [
    path("signup/", UserSignup.as_view(), name="signup"),
    path("login/", UserLogin.as_view(), name="login"),
    path("logout/", UserLogout.as_view(), name="logout"),
]
