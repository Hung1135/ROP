from django.contrib import admin
from .models import users, Cvs, Job, Applications

@admin.register(users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'email', 'phone', 'role', 'created_at')
    search_fields = ('fullname', 'email', 'phone')
    list_filter = ('role',)

@admin.register(Cvs)
class CvsAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'uploaded_at')
    search_fields = ('full_name', 'email')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'location', 'category', 'end_date')
    search_fields = ('title', 'company', 'skills')
    list_filter = ('category',)

@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'job', 'status', 'applied_at', 'is_sent')
    list_filter = ('status', 'is_sent')