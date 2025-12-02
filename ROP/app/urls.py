from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin_filter', views.filter),
    path('admin_post_detail', views.post_detail),
    path('login', views.login),
    path('home', views.homeUser),
    path('ChangePassword', views.ChangePassword),
    path('user_detailPost', views.detailPost),
    path('user_personalprofile', views.personalprofile),
]