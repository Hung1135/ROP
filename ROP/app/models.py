from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class users (models.Model):
    id=models.AutoField(primary_key=True)
    fullname=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    password_hash=models.CharField(max_length=100)
    role=models.BooleanField()
    created_at=models.DateField(auto_now_add=True)
    def __str__(self):
        return self.fullname
    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
    class Meta:
        
        db_table = 'users'
        managed = False

class Cvs(models.Model):
    id = models.AutoField(primary_key=True)

    candidate_id = models.IntegerField()

    file_name = models.CharField(max_length=255)

    file_path = models.CharField(max_length=500)

    extract_text =models.CharField(max_length=500)

    upload_at = models.DateField(auto_now=True)

    class Meta:
        db_table = 'cvs'
        managed = False

    def __str__(self):
        return self.file_name

class Job(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    work_type = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    requirements = models.CharField(max_length=255, null=True, blank=True)
    skills = models.CharField(max_length=255, null=True, blank=True)
    benefit = models.CharField(max_length=255, null=True, blank=True)
    create_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'jobs'
        managed = False