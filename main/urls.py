from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("home/", views.default, name='default'),
    path("playlist/", views.playlist, name='your_playlists'),
    path("search/", views.search, name='search_page'),
    path("login/",views.logIn_view, name="login"),
    path('signup/',views.register_view,  name="signup"),
    path('logout/', views.logoutview, name = "logout"),
    path('forget-password/',views.Forget_password, name="forget_password"),
    path('change-password/<token>/', views.changepassword , name = "change_password"),
]