from django.contrib import admin
from django.urls import path
from app import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('user_detailPost/<int:id>/', views.detailPost, name='detailPost'),
    path('user_personalprofile', views.personalprofile, name='user_personalprofile'),
    path('appliedJobsList', views.appliedJobsList, name='appliedJobsList'),
    path('search',views.search,name='search'),

    path('upload_cv/', views.upload_cv, name='upload_cv'),
    path('apply_job/<int:job_id>/', views.apply_job, name='apply_job'),


    path('cv/<int:id>/', views.cv_detail, name='cv_detail'),
    path('cv/pdf/<int:id>/', views.cv_pdf, name='cv_pdf'),
path('cv/json/<int:id>/', views.cv_detail_json, name='cv_detail_json'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)