from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from django.template.defaultfilters import title
from django.db.models import Q


from django.utils import timezone
from django.shortcuts import render, redirect
from django.conf import settings
# from .forms import UploadCVForm
from django.utils import timezone
from django.utils import timezone
from .models import Cvs, Applications, Job, users
from django.http import FileResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .models import *

from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
import re
from django.shortcuts import render
# Create your views here.
# admin

def split_text(text):
    if not text:
        return []
    return [x.strip() for x in re.split(r'\n|\. ', text) if x.strip()]

def post_detail(request, id):
    job = Job.objects.get(id=id)  # Giữ nguyên get()

    jobDescript = split_text(job.description)
    jobRequire = split_text(job.requirements)
    jobSkill = split_text(job.skills)
    jobBenefit = split_text(job.benefit)

    return render(request, 'admin/post_detail.html', {
        'job': job,
        "jobDescript": jobDescript,
        "jobRequire": jobRequire,
        "jobSkill": jobSkill,
        "jobBenefit": jobBenefit
    })


def ListJob(request):
    user_id = request.session.get('user_id')
    # if request.method == 'GET':
    #     if not user_id:
    #         return redirect('login')
    # jobs = Job.objects.all().filter(user=user_id)
    jobs = Job.objects.all()
    return render(request, 'admin/ListJob.html', {'jobs': jobs})


def manaPostCV(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    cvs = Cvs.objects.select_related('user').all()
    return render(request, 'admin/managePostCV.html', {'cvs': cvs})

# logout
def logout_user(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_full_name' in request.session:
        del request.session['user_full_name']
    if 'user_role' in request.session:
        del request.session['user_role']
    return redirect('login')


# login
def login(request):
    if 'user_id' in request.session:
        user_role = request.session.get('user_role')

        if user_role:
            return redirect('ListJob')
        else:
            return redirect('home')
    if request.method == 'POST' and 'full_name' in request.POST:

        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        selected_role = request.POST.get('role', 'candidate')
        if selected_role == 'employer':
            is_admin = True
        else:
            is_admin = False

        if password != confirm_password:
            messages.error(request, "Mật khẩu và xác nhận mật khẩu không khớp!")
            return render(request, 'login/login.html')

        hashed_password = make_password(password)

        try:
            users.objects.create(
                fullname=full_name,
                email=email,
                phone=phone,
                password_hash=hashed_password,
                role=is_admin
            )
            messages.success(request, "Đăng ký thành công! Vui lòng Đăng nhập.")
            return redirect('login')
        except IntegrityError:
            messages.error(request, "Email hoặc Số điện thoại đã tồn tại\nVui lòng thử lại.")
            return render(request, 'login/login.html')
        except Exception as e:
            messages.error(request, f"Đã có lỗi xảy ra trong quá trình đăng ký: {e}")
            return render(request, 'login/login.html')

    elif request.method == 'POST' and 'email_login' in request.POST:
        email = request.POST.get('email_login')
        password = request.POST.get('password_login')

        try:
            user = users.objects.get(email=email)
        except users.DoesNotExist:
            messages.error(request, "Email hoặc mật khẩu không đúng.")
            return render(request, 'login/login.html')

        if check_password(password, user.password_hash):

            request.session['user_id'] = user.id
            request.session['user_full_name'] = user.fullname
            request.session['user_role'] = user.role

            if user.role:
                return redirect('ListJob')
            else:
                return redirect('home')
        else:
            messages.error(request, "Email hoặc mật khẩu không đúng.")
            return render(request, 'login/login.html')

    return render(request, 'login/login.html')


# user
def homeUser(request):
    # if request.method == 'GET':
    #     user_id = request.session.get('user_id')
    #     if not user_id:
    #         return redirect('login')
    sort = request.GET.get('sort', 'newest')
    order_by = 'create_at' if sort == 'oldest' else '-create_at'
    jobs = Job.objects.all().order_by(order_by)
    return render(request, 'user/home.html', {'jobs': jobs, 'sort': sort})

def _is_django_hash(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if "$" not in value:
        return False
    algo = value.split("$", 1)[0]
    return algo in {"pbkdf2_sha256", "pbkdf2_sha1", "argon2", "bcrypt_sha256", "scrypt"}


def ChangePassword(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = users.objects.filter(id=user_id).first()
    if not user:
        return redirect('login')

    if request.method == 'POST':
        old_password = request.POST.get('old_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not old_password or not new_password or not confirm_password:
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
            return render(request, 'user/ChangePassword.html')

        stored = user.password_hash or ""
        if _is_django_hash(stored):
            ok_old = check_password(old_password, stored)
        else:
            ok_old = (old_password == stored)

        if not ok_old:
            messages.error(request, "Sai mật khẩu hiện tại.")
            return render(request, 'user/ChangePassword.html')

        if new_password != confirm_password:
            messages.error(request, "Mật khẩu mới và nhập lại mật khẩu không khớp.")
            return render(request, 'user/ChangePassword.html')
        user.password_hash = make_password(new_password)
        user.save(update_fields=['password_hash'])

        messages.success(request, "Đổi mật khẩu thành công!")
        return redirect('home')

    return render(request, 'user/ChangePassword.html')


def detailPost(request, id):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

    job = Job.objects.get(id=id)  # Giữ nguyên get()

    jobDescript = split_text(job.description)
    jobRequire = split_text(job.requirements)
    jobSkill = split_text(job.skills)
    jobBenefit = split_text(job.benefit)

    context = {
        'job': job,
        'jobDescript': jobDescript,
        'jobRequire': jobRequire,
        'jobSkill': jobSkill,
        'jobBenefit': jobBenefit
    }

    return render(request, 'user/detailPost.html', context)


def personalprofile(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    user_id=request.session.get('user_id')
    user = users.objects.get(id=user_id)
    if request.method == 'POST':
        user.fullname = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.birthday = request.POST.get('birthday')
        user.sex=request.POST.get("sex")
        user.save()
        return render(request, 'user/personalprofile.html', {"user": user,"notify":"thành công"})

    return render(request, 'user/personalprofile.html',{"user": user})


def appliedJobsList(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    return render(request, 'user/appliedJobsList.html')


# cái này db
def functionPost(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    if request.method == 'POST':
        title = request.POST.get('title')
        company_name = request.POST.get('company_name')
        location = request.POST.get('location')
        salary_min = request.POST.get('salary_min')
        salary_max = request.POST.get('salary_max')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        skills = request.POST.get('skills')
        benefits = request.POST.get('benefits')
        user_id = request.session.get('user_id')
        user_obj = get_object_or_404(users, id=user_id)
        Job.objects.create(
            title=title,
            company=company_name,
            location=location,
            salary_min=int(salary_min) if salary_min else None,
            salary_max=int(salary_max) if salary_max else None,
            description=description,
            requirements=requirements,
            benefit=benefits,
            skills=skills,
            user=user_obj
        )
        messages.success(request, 'Đăng tin tuyển dụng thành công!')
        return redirect('ListJob')
    return render(request, 'admin/functionPost.html')


def search(request):
    if request.method == 'GET':
        boxSearch = request.GET.get('boxsearch', '').strip()
        jobs = Job.objects.all()
        if boxSearch:
            salary_q = Q()
            try:
                salary_value = int(boxSearch)
                salary_q = Q(salary_min__lte=salary_value) & Q(salary_max__gte=salary_value)
            except ValueError:
                pass
            jobs = jobs.filter(
                Q(title__icontains=boxSearch) |
                Q(company__icontains=boxSearch) |
                Q(location__icontains=boxSearch) |
                salary_q
            )
    return render(request, 'user/home.html', {'jobs': jobs, "bs": boxSearch})

def upload_cv(request):
    if request.method == 'POST':
        file = request.FILES['file']
        custom_user = users.objects.get(id=request.session['user_id'])
        cvs = Cvs(
            user=custom_user,
            file=file,
            file_name=file.name
        )
        cvs.save()
        return redirect('appliedJobsList')
    return redirect('home')

def apply_job(request, job_id):
    if request.method == 'POST':
        file = request.FILES['file']

        custom_user = users.objects.get(id=request.session['user_id'])

        # Lưu CV
        cv = Cvs.objects.create(
            user=custom_user,
            file=file,
            file_name=file.name,
            uploaded_at=timezone.now()
        )

        # Tạo record ứng tuyển
        Applications.objects.create(
            job_id=job_id,
            cv=cv,
            user=custom_user,
            applied_at=timezone.now(),
            status='new'
        )

        return redirect('appliedJobsList')
    return redirect('home')

def appliedJobsList(request):
    # Lấy user hiện tại từ session
    custom_user = users.objects.get(id=request.session['user_id'])

    # Lấy tất cả applications của user này, join sang job để lấy thông tin
    applications = Applications.objects.filter(user=custom_user).select_related('job').order_by('-applied_at')

    return render(request, 'user/appliedJobsList.html', {'applications': applications})

@xframe_options_sameorigin
def cv_detail(request, id):
    cv = get_object_or_404(Cvs, id=id)
    # kiểm tra file có phải PDF không
    is_pdf = cv.file_name.lower().endswith(".pdf")
    print(cv.file.url)
    return render(request, 'admin/cv_detail.html', {'cv': cv, 'is_pdf': is_pdf})

def cv_pdf(request, id):
    cv = get_object_or_404(Cvs, id=id)
    if not cv.file:
        raise Http404("No file")
    f = cv.file.open('rb')
    response = FileResponse(f, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{cv.file_name}"'
    # Cho phép nhúng cùng origin
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

