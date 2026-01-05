from time import timezone
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


# Create your models here.
class users(models.Model):
    id = models.AutoField(primary_key=True)
    fullname = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=100)
    role = models.BooleanField()
    created_at = models.DateField(auto_now_add=True)
    sex=models.CharField(max_length=100)
    birthday = models.DateField()

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
    user = models.ForeignKey(
        users,
        on_delete=models.CASCADE,
        null=True, blank=True,
    )
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    skills = models.TextField()
    description = models.TextField()
    uploaded_at = models.DateField(auto_now_add=True)

    class Meta: 
        db_table = 'cvs'
        managed = False

class Job(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        users,
        on_delete=models.DO_NOTHING,
        db_column='user_id',
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    end_date = models.DateField()
    description = models.CharField(max_length=255, null=True, blank=True)
    requirements = models.CharField(max_length=255, null=True, blank=True)
    skills = models.CharField(max_length=255, null=True, blank=True)
    benefit = models.CharField(max_length=255, null=True, blank=True)
    create_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'jobs'
        managed = False

    def __str__(self):
        return self.title
from django.db import models
from django.utils import timezone

class Applications(models.Model):
    id = models.AutoField(primary_key=True)
    job = models.ForeignKey( Job, on_delete=models.CASCADE, db_column='job_id')
    cv = models.ForeignKey(Cvs,  on_delete=models.CASCADE, db_column='cv_id' )
    user = models.ForeignKey(users, on_delete=models.CASCADE, db_column='user_id')
    applied_at =  models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('rejected', 'Rejected'),
            ('passed', 'Passed'),
        ],
        default='new'
    )
    employer_note = models.CharField(max_length=255, null=True, blank=True)
    ai_score = models.CharField(max_length=255, null=True, blank=True)
    manual_rank = models.CharField(max_length=255, null=True, blank=True)
    is_sent = models.BooleanField(default=False) # Thêm dòng này


    class Meta:
        db_table = 'applications'
        managed = False

    def __str__(self):
        return f"{self.user.fullname} - {self.job.title} ({self.status})"


