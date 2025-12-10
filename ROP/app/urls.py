from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    #path('', views.filter, name='admin_filter'),
    
    path('home', views.homeAdmin, name='admin_filter'),
    path('ListJob', views.ListJob, name='ListJob'),
    path('admin_post_detail', views.post_detail, name='admin_post_detail'),

    path('login', views.login, name='login'),

    path('', views.homeUser, name='home'),
    path('ChangePassword', views.ChangePassword, name='ChangePassword'),
    path('user_detailPost', views.detailPost, name='detailPost'),
    path('user_personalprofile', views.personalprofile, name='user_personalprofile'),
    path('appliedJobsList', views.appliedJobsList, name='appliedJobsList'),
]