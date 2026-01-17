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
    # path('cv/json/<int:id>/', views.cv_detail_json, name='cv_detail_json'),

    path('send_interview_email/<int:app_id>/', views.send_interview_email, name='send_interview_email'),
    # path('cv_form/<int:cv_id>/', views.cv_detail_form, name='cv_detail_form'),
    path('search/', views.search, name='search'),
    path('cv/create/', views.create_cv, name='create_cv'),
    path('cv/list/', views.cv_list, name='cv_list'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/featured/', views.featured_companies, name='featured_companies'), 
    path('matching-jobs/', views.matching_jobs_for_cv, name='matching_jobs'),
    path('cv/<int:id>/', views.cv_detail, name='cv_detail'),
    path('cv_form/<int:cv_id>/', views.cv_detail_form, name='cv_detail_form'),
    path('cv_form_user/<int:cv_id>/', views.cv_detail_form_user, name='cv_form_user'),

    path("applications/<int:app_id>/download/", views.application_pdf_download, name="application_pdf_download"),
    path("test-font/", views.test_font, name="test_font"),
    path("test-pdf/", views.test_pdf_font, name="test_pdf_font"),



       ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


