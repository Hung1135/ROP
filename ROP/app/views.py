from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse

from django.contrib import messages 
from .models import User 
from django.contrib.auth.hashers import make_password, check_password 
from django.db.utils import IntegrityError

# Create your views here.
#admin
def filter(request):
    return render(request, 'admin/ad_filter.html')

def post_detail(request):
    return render(request, 'admin/post_detail.html')

#login
def logout_user(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_full_name' in request.session:
        del request.session['user_full_name']
    if 'user_role' in request.session:
        del request.session['user_role']
        
    return redirect('login/')

def login(request):
    if 'user_id' in request.session:
        user_role = request.session.get('user_role')
        if user_role == 'admin':
            return redirect('admin_dashboard') 
        elif user_role == 'employer':
            return redirect('admin_filter') 
        else: # candidate
            return redirect('home')
        
    if request.method == 'POST' and 'full_name' in request.POST:
       
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password') 
        role = request.POST.get('role', 'candidate') 

        if password != confirm_password:
            messages.error(request, "Mật khẩu và xác nhận mật khẩu không khớp!")
            return render(request, 'login/login.html') 

        hashed_password = make_password(password)

        try:
            User.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                password_hash=hashed_password,
                role=role
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
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email hoặc mật khẩu không đúng.")
            return render(request, 'login/login.html')

        if check_password(password, user.password_hash):
            # Thiết lập session
            request.session['user_id'] = user.id
            request.session['user_full_name'] = user.full_name
            request.session['user_role'] = user.role
            
            
            if user.role == 'admin':
                return redirect('admin_dashboard') 
            elif user.role == 'employer':
                return redirect('admin_filter') 
            else: # candidate
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

# hồ sơ cá nhân
def personalprofile(request):
    if 'user_id' not in request.session:
        messages.warning(request, "Vui lòng đăng nhập để truy cập Hồ sơ.")
        return redirect('login')

    user_id = request.session['user_id']
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Không tìm thấy thông tin người dùng.")
        return redirect('logout') 
    
    context = {
        'user': user,
    }
    return render(request, 'user/personalprofile.html', context)
    
def appliedJobsList(request):
    return render(request, 'user/appliedJobsList.html')
