from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin_filter', views.filter, name='admin_filter'),
    path('admin_post_detail', views.post_detail, name='admin_post_detail'),
    path('login', views.login, name='login'),
    path('home', views.homeUser, name='home'),
    path('ChangePassword', views.ChangePassword, name='ChangePassword'),
    path('user_detailPost', views.detailPost, name='detailPost'),
    path('user_personalprofile', views.personalprofile, name='user_personalprofile'),
    path('appliedJobsList', views.appliedJobsList, name='appliedJobsList'),
]