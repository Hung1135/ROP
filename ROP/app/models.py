from time import timezone
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from difflib import SequenceMatcher

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
def similarity(a, b):
    return SequenceMatcher(None, a or "", b or "").ratio()
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
    category = models.CharField(max_length=100, null=True, blank=True) 

    class Meta:
        db_table = 'jobs'
        managed = False

    def __str__(self):
        return self.title
    def job_categories(request):
    # Lấy danh sách các ngành nghề không trùng lặp từ DB
        categories = Job.objects.values_list('category', flat=True).distinct()

    def clean(self):
        today = timezone.now().date()
        if self.salary_min is not None and self.salary_min < 0:
            raise ValidationError("❌ Lương tối thiểu không được là số âm.")

        if self.salary_max is not None and self.salary_max < 0:
            raise ValidationError("❌ Lương tối đa không được là số âm.")

            # ====== 2️⃣ MIN < MAX ======
        if self.salary_min is not None and self.salary_max is not None:
            if self.salary_min >= self.salary_max:
                raise ValidationError(
                    "❌ Lương tối thiểu phải nhỏ hơn lương tối đa."
                )
        # 1️⃣ Tối đa 5 bài / ngày
        if not self.pk:
            count_today = Job.objects.filter(
                user=self.user,
                create_at=today
            ).count()
            if count_today >= 5:
                raise ValidationError("❌ Mỗi ngày chỉ được đăng tối đa 5 bài.")

        # 2️⃣ Độ dài nội dung
        if not (10 <= len(self.title) <= 100):
            raise ValidationError("❌ Tiêu đề phải từ 10–100 ký tự.")

        if len(self.description) < 50:
            raise ValidationError("❌ Mô tả phải ≥ 50 ký tự.")

        if len(self.requirements) < 50:
            raise ValidationError("❌ Yêu cầu phải ≥ 50 ký tự.")

        # 3️⃣ Trùng title + company + location (chỉ khi bài cũ còn hạn)
        qs = Job.objects.filter(
            user=self.user,
            title=self.title,
            company=self.company,
            location=self.location,
            end_date__gte=today
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError(
                "❌ Bài trùng tiêu đề + công ty + địa điểm, chỉ được đăng khi bài cũ hết hạn."
            )

        # 4️⃣ Nội dung giống > 80%
        active_jobs = Job.objects.filter(
            user=self.user,
            end_date__gte=today
        )
        if self.pk:
            active_jobs = active_jobs.exclude(pk=self.pk)

        for job in active_jobs:
            if similarity(job.description, self.description) > 0.8:
                raise ValidationError(
                    "❌ Nội dung giống > 80% bài trước, chỉ được đăng khi bài cũ hết hạn."
                )

        # 5️⃣ Không cho sửa nếu đã có ứng viên
        if self.pk:
            old = Job.objects.get(pk=self.pk)
            if Applications.objects.filter(job=old).exists():
                fields = ['title', 'description', 'requirements', 'company', 'location']
                for f in fields:
                    if getattr(old, f) != getattr(self, f):
                        raise ValidationError(
                            "❌ Bài đăng đã có ứng viên, không được sửa nội dung chính."
                        )

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
    is_rejected = models.BooleanField(default=False)  # đã từ chối hay chưa



    class Meta:
        db_table = 'applications'
        managed = False

    def __str__(self):
        return f"{self.user.fullname} - {self.job.title} ({self.status})"


