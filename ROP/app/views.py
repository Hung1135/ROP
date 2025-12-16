from django.contrib import messages
from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import *

from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
# Create your views here.
# admin
def post_detail(request, id):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    job = Job.objects.get(id=id)
    return render(request, 'admin/post_detail.html', {'job': job})


def ListJob(request):
    user_id = request.session.get('user_id')
    if request.method == 'GET':
        if not user_id:
            return redirect('login')
    jobs = Job.objects.filter(user=user_id)
    return render(request, 'admin/ListJob.html', {'jobs': jobs})


def manaPostCV(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    return render(request, 'admin/managePostCV.html')

#logout
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
            messages.error(request, "Email hoặc Số điện thoại đã tồn tại. Vui lòng thử lại.")
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


def detailPost(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    return render(request, 'user/detailPost.html')
def personalprofile(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    return render(request, 'user/personalprofile.html')


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
        user_id = request.session.get('id')
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
            user_id=user_id
        )
        messages.success(request, 'Đăng tin tuyển dụng thành công!')
        return redirect('ListJob')
    return render(request, 'admin/functionPost.html')
