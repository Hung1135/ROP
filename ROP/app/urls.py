from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    #path('', views.filter, name='admin_filter'),

    path('ListJob', views.ListJob, name='ListJob'),
    path('admin_post_detail/<int:id>/', views.post_detail, name='admin_post_detail'),
    path('functionPost', views.functionPost, name='functionPost'),
    path('manaPostCV', views.manaPostCV, name='manaPostCV'),

    path('', views.login, name='login'),
    path('logout', views.logout_user, name='logout'),

    path('home', views.homeUser, name='home'),
    path('ChangePassword', views.ChangePassword, name='ChangePassword'),
    path('user_detailPost', views.detailPost, name='detailPost'),
    path('user_personalprofile', views.personalprofile, name='user_personalprofile'),
    path('appliedJobsList', views.appliedJobsList, name='appliedJobsList'),
]