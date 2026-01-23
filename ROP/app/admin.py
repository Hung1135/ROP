from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils import timezone
from difflib import SequenceMatcher

from .models import users, Cvs, Job, Applications

@admin.register(users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'email', 'phone', 'role', 'created_at')
    search_fields = ('fullname', 'email', 'phone')
    list_filter = ('role',)

def has_applications(job):
    return Applications.objects.filter(job=job).exists()


def similarity(a, b):
    return SequenceMatcher(None, a or "", b or "").ratio()
@admin.register(Cvs)
class CvsAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'phone', 'uploaded_at')
    search_fields = ('full_name', 'email')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'location', 'category', 'end_date')
    search_fields = ('title', 'company', 'skills')
    list_filter = ('category',)


    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

@admin.register(Applications)
class ApplicationsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'job', 'status', 'applied_at', 'is_sent')
    list_filter = ('status', 'is_sent')
