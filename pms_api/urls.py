"""
URL configuration for pms_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from pms_app.views import RegisterView,LoginView,LogoutView,MeView,UserDetailView,UserListView,TeamMemberListCreateView,TeamMemberDetailView,ProjectListCreateView, ProjectDetailView, ProjectTasksView, TaskListCreateView, TaskDetailView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register', RegisterView.as_view(), name='auth_register'),
    path('api/auth/login', LoginView.as_view(), name='auth_login'),
    path('api/auth/me', MeView.as_view(), name='auth_me'),
    path('api/auth/logout', LogoutView.as_view(), name='auth_logout'),
    path('api/users', UserListView.as_view(), name='User_List'),
    path('api/users/<id>', UserDetailView.as_view(), name='Single_User'),
    path('api/team_members', TeamMemberListCreateView.as_view(), name='team_member_list_CR'),
    path('api/team_members/<id>', TeamMemberDetailView.as_view(), name='team_memebr_details_view_UD'),

    path('api/projects', ProjectListCreateView.as_view(), name='project_list_CR'),
    path('api/projects/<p_id>', ProjectDetailView.as_view(), name='project_details_view_UD'),
    path('api/task', TaskListCreateView.as_view(), name='Create Task View'),
    path('api/task/<t_id>', TaskDetailView.as_view(), name='TaskDetailView'),


    




    # path("api-auth/", include("rest_framework.urls"))
    # path("api/", include("pms_app.urls")),

]
