from django.contrib import messages
from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError

# Create your views here.
#admin
def homeAdmin(request):
    return render(request, 'admin/home.html')

def post_detail(request):
    return render(request, 'admin/post_detail.html')

def ListJob(request):
    return render(request, 'admin/ListJob.html')

def manaPostCV(request):
    return render(request, 'admin/managePostCV.html')


#logout
def logout_user(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_full_name' in request.session:
        del request.session['user_full_name']
    if 'user_role' in request.session:
        del request.session['user_role']
    return redirect('login/')

#login

def login(request):
    if 'user_id' in request.session:
        user_role = request.session.get('user_role') 
        
        if user_role:
            return redirect('admin_filter') 
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
                return redirect('admin_filter') 
            else: 
                return redirect('home')
        else:
            messages.error(request, "Email hoặc mật khẩu không đúng.")
            return render(request, 'login/login.html')

    return render(request, 'login/login.html')
# user
def homeUser(request):
    return render(request, 'user/home.html')

def ChangePassword(request):
    return render(request, 'user/ChangePassword.html')

def detailPost(request):
    return render(request, 'user/detailPost.html')

def personalprofile(request):
    return render(request, 'user/personalprofile.html')
def appliedJobsList(request):
    return render(request, 'user/appliedJobsList.html')
def functionPost(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        company_name = request.POST.get('company_name')  # bạn ghi trong form là company_name
        location = request.POST.get('location')
        salary_min = request.POST.get('salary_min')
        salary_max = request.POST.get('salary_max')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        benefits = request.POST.get('benefits')
        Job.objects.create(
            title=title,
            company=company_name,
            location=location,
            salary_min=int(salary_min) if salary_min else None,
            salary_max=int(salary_max) if salary_max else None,
            description=description,
            requirements=requirements,
            benefit=benefits,
        )
        messages.success(request, 'Đăng tin tuyển dụng thành công!')
        return redirect('ListJob')
    return render(request, 'admin/functionPost.html')








