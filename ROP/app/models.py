from django.db import models

# Create your models here.
class users (models.Model):
    id=models.AutoField(primary_key=True)
    fullname=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    password_hash=models.CharField(max_length=100)
    role=models.BooleanField()
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.fullname
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
