from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("account", views.account, name="account"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("search", views.search, name="search")
]