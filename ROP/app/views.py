from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.template.defaultfilters import title
from django.db.models import Q
from .AI.cv_matcher import extract_cv_text, match_cv_fields
# from .AI.cv_matcher import  match_cv_with_job
from .models import Applications, Job, Cvs
from django.utils import timezone
from django.shortcuts import render, redirect
from django.conf import settings
from .models import Cvs, Applications, Job, users
from django.http import FileResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_sameorigin
from .models import *
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
import re
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .AI.utils import classify_job_category
from django.shortcuts import render
from django.db.models import Q
from .models import Job
from django.db.models import Count  
# Create your views here.
# admin

def split_text(text):
    if not text:
        return []
    return [x.strip() for x in re.split(r'\n|\. ', text) if x.strip()]


def post_detail(request, id):
    job = Job.objects.get(id=id)

    cv_analyses = analyze_cvs_for_job(job)

    return render(request, 'admin/post_detail.html', {
        'job': job,
        'jobDescript': split_text(job.description),
        'jobRequire': split_text(job.requirements),
        'jobSkill': split_text(job.skills),
        'jobBenefit': split_text(job.benefit),
        'cv_analyses': cv_analyses,
        'total_cvs': len(cv_analyses),
    })


# Lấy tất cả Applications của job, extract CV, tính score, lưu vào DB.
# Lấy tất cả Applications của job, tính score dựa trên dữ liệu form (không cần file PDF)
def analyze_cvs_for_job(job):
    applications = Applications.objects.filter(job=job).select_related('cv', 'user')
    results = []

    for app in applications:
        cv = app.cv

        # Chuẩn bị dữ liệu từng field từ form
        cv_data = {
            "description": cv.description or "",
            "skills": cv.skills or "",
            "address": cv.address or ""
        }

        # Tính điểm chi tiết theo trọng số: requirements 50%, skills 40%, location 10%
        score, level, field_scores = match_cv_fields(cv_data, job)

        # Lưu AI score vào Applications
        app.ai_score = f"{score} ({level})"
        app.save(update_fields=['ai_score'])

        results.append({
            "application": app,
            "cv": cv,
            "score": score,
            "match_level": level,
            "field_scores": field_scores,  # điểm từng phần: requirements, skills, location
            "parsed": {
                "name": app.user.fullname,
                "email": app.user.email
            },
            "display_name": app.user.fullname or "Chưa xác định"
        })

    return results


def cv_detail_json(request, id):
    cv = get_object_or_404(Cvs, id=id)
    job_id = request.GET.get("job_id")
    score_data = None
    if job_id:
        job = get_object_or_404(Job, id=job_id)
        cv_data = {
            "description": cv.description,
            "skills": cv.skills,
            "address": cv.address
        }
        total_score, level, field_scores = match_cv_fields(cv_data, job)
        score_data = {
            "total_score": total_score,
            "level": level,
            "field_scores": field_scores
        }

    return JsonResponse({
        "full_name": cv.full_name,
        "email": cv.email,
        "phone": cv.phone,
        "address": cv.address,
        "description": cv.description,
        "skills": cv.skills,
        "score_data": score_data
    })



def ListJob(request):
    user_id = request.session.get('user_id')
    # if request.method == 'GET':
    #     if not user_id:
    #         return redirect('login')
    jobs = Job.objects.all().filter(user=user_id)
    # jobs = Job.objects.all()
    return render(request, 'admin/ListJob.html', {'jobs': jobs})


# def manaPostCV(request):
#     if request.method == 'GET':
#         user_id = request.session.get('user_id')
#         if not user_id:
#             return redirect('login')
#     cvs = Cvs.objects.select_related('user').all()
#     return render(request, 'admin/managePostCV.html', {'cvs': cvs})
def manaPostCV(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    # Lấy tất cả CV ứng tuyển vào các job do user này đăng
    cvs = Cvs.objects.filter(
        applications__job__user_id=user_id
    ).select_related('user').distinct()

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
            request.session['user_email'] = user.email

            if user.email == "admin@gmail.com":
                return redirect('admin_manage_candidates') # Admin nên vào thẳng trang quản lý
            elif user.role:
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
    today = timezone.now().date()
    job = Job.objects.get(id=id)  # Giữ nguyên get()
    user_cvs = Cvs.objects.filter(user=user_id) 
    user_cvs = Cvs.objects.filter(user_id=user_id)
    is_active = job.create_at <= today <= job.end_date
    jobDescript = split_text(job.description)
    jobRequire = split_text(job.requirements)
    jobSkill = split_text(job.skills)
    jobBenefit = split_text(job.benefit)

    context = {
        'job': job,
        'jobDescript': jobDescript,
        'jobRequire': jobRequire,
        'jobSkill': jobSkill,
        'jobBenefit': jobBenefit,
        'is_active': is_active,
        'user_cvs': user_cvs, 
    }

    return render(request, 'user/detailPost.html', context)


def personalprofile(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    user_id = request.session.get('user_id')
    user = users.objects.get(id=user_id)
    if request.method == 'POST':
        user.fullname = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.birthday = request.POST.get('birthday')
        user.sex = request.POST.get("sex")
        user.save()
        return render(request, 'user/personalprofile.html', {"user": user, "notify": "thành công"})

    return render(request, 'user/personalprofile.html', {"user": user})


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
        end_date = request.POST.get('end_date')
        category = classify_job_category(title, skills, description)
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
            end_date=end_date,
            category = classify_job_category(title, skills, description),
            user=user_obj
        )
        messages.success(request, 'Đăng tin tuyển dụng thành công!')
        return redirect('ListJob')
    return render(request, 'admin/functionPost.html')


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


# def apply_job(request, job_id):
#     if request.method == 'POST':
#         file = request.FILES['file']
#
#         custom_user = users.objects.get(id=request.session['user_id'])
#
#         # Lưu CV
#         cv = Cvs.objects.create(
#             user=custom_user,
#             file=file,
#             file_name=file.name,
#             uploaded_at=timezone.now()
#         )
#
#         # Tạo record ứng tuyển
#         Applications.objects.create(
#             job_id=job_id,
#             cv=cv,
#             user=custom_user,
#             applied_at=timezone.now(),
#             status='new'
#         )
#
#         return redirect('appliedJobsList')
#     return redirect('home')

def apply_job(request, job_id):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

        custom_user = users.objects.get(id=user_id)

        # Lấy dữ liệu từ form
        fullname = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        description = request.POST.get('description', '').strip()
        skills = request.POST.get('experience', '').strip()  # form field "Kỹ năng" mapping vào skills

        # Lưu thông tin vào Cvs
        cv = Cvs.objects.create(
            user=custom_user,
            full_name=fullname,
            email=email,
            phone=phone,
            address=address,
            description=description,
            skills=skills,
            uploaded_at=timezone.now()
        )

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
    custom_user = users.objects.get(id=request.session['user_id'])

    applications = Applications.objects.filter(user=custom_user).select_related('job').order_by('-applied_at')

    return render(request, 'user/appliedJobsList.html', {'applications': applications})


@xframe_options_sameorigin
def cv_detail(request, id):
    cv = get_object_or_404(Cvs, id=id)
    return render(request, 'admin/cv_detail.html', {'cv': cv})


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

def send_interview_email(request, app_id):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            application = get_object_or_404(Applications, id=app_id)
            user_candidate = application.user
            job = application.job

            itv_time = request.GET.get('time', 'Sẽ thông báo sau')
            itv_location = request.GET.get('location', 'Tại văn phòng công ty')
            itv_docs = request.GET.get('docs', 'Không yêu cầu')
            itv_contact = request.GET.get('contact', 'Phòng nhân sự') 

            subject = f"[Mời phỏng vấn] Vị trí {job.title} - {job.company}"
            
            message = f"""
            Chào {user_candidate.fullname},

            Chúng tôi đã nhận được hồ sơ của bạn cho vị trí {job.title}. 
            Dựa trên đánh giá chuyên môn, chúng tôi trân trọng mời bạn tham gia buổi phỏng vấn.

            CHI TIẾT BUỔI PHỎNG VẤN:
            - Thời gian: {itv_time}
            - Địa điểm: {itv_location}
            - Tài liệu cần chuẩn bị: {itv_docs}
            - Thông tin liên hệ nếu có thắc mắc: {itv_contact}

            Vui lòng phản hồi email này để xác nhận sự tham gia của bạn.
            
            Trân trọng,
            Phòng nhân sự {job.company}.
            """
            
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user_candidate.email]

            send_mail(subject, message, email_from, recipient_list)
            
            application.is_sent = True
            application.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


from django.shortcuts import render, get_object_or_404
from .models import Cvs

def cv_detail_form(request, cv_id):
    cv = get_object_or_404(Cvs, id=cv_id)
    return render(request, 'admin/detail.html', {'cv': cv})

def cv_detail_form_user(request, cv_id):
    cv = get_object_or_404(Cvs, id=cv_id)
    return render(request, 'user/detail.html', {'cv': cv})

# them
def job_list_user(request):
    query = request.GET.get('boxsearch', '').strip()
    location = request.GET.get('location', '').strip()
    salary_range = request.GET.get('salary_range', '')
    sort = request.GET.get('sort', 'newest')

    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(company__icontains=query))

    if location:
        jobs = jobs.filter(location__icontains=location)

    if salary_range == '10-20':
        jobs = jobs.filter(salary_min__gte=10, salary_max__lte=20)
    elif salary_range == '20+':
        jobs = jobs.filter(salary_min__gte=20)

    order_by = 'create_at' if sort == 'oldest' else '-create_at'
    jobs = jobs.order_by(order_by)

    locations = Job.objects.values_list('location', flat=True).distinct()

    return render(request, 'user/job_list.html', {
        'jobs': jobs,
        'locations': locations,
        'current_loc': location,
        'current_salary': salary_range,
        'sort': sort,
        'bs': query
    })

from django.db.models import Q 

def home_view(request):
    jobs = Job.objects.all().order_by('-create_at')[:10]
    return render(request, 'home.html', {'jobs': jobs})

def search(request):
    boxSearch = request.GET.get('boxsearch', '').strip()
    location_filter = request.GET.get('location', '').strip()
    salary_range = request.GET.get('salary_range', '')
    category_filter = request.GET.get('category', '').strip()
    sort = request.GET.get('sort', 'newest')

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

    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)

    if category_filter:
        jobs = jobs.filter(category=category_filter)

    if salary_range == '10-20':
        jobs = jobs.filter(salary_min__gte=10, salary_max__lte=20)
    elif salary_range == '20+':
        jobs = jobs.filter(salary_min__gte=20)

    if sort == 'oldest':
        jobs = jobs.order_by('create_at')
    else:
        jobs = jobs.order_by('-create_at')

    provinces = [
        "An Giang", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh", "Bến Tre", "Bình Định", 
        "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", 
        "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", 
        "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang", 
        "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", 
        "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", 
        "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", 
        "Tiền Giang", "TP.HCM", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
    ]
    
    categories = Job.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct()

    return render(request, 'user/job_list.html', {
        'jobs': jobs,
        'bs': boxSearch,
        'provinces': provinces,
        'categories': categories,
        'current_loc': location_filter,
        'current_salary': salary_range,
        'current_cat': category_filter,
        'sort': sort
    })

def company_list(request):
    all_companies = Job.objects.exclude(company__isnull=True).exclude(company='') \
        .values('company') \
        .annotate(num_jobs=Count('id')) \
        .order_by('company') # Sắp xếp A-Z

    return render(request, 'user/company_list.html', {
        'companies': all_companies
    })


def featured_companies(request):
    top_companies = Job.objects.exclude(company__isnull=True).exclude(company='') \
        .values('company') \
        .annotate(num_jobs=Count('id')) \
        .order_by('-num_jobs') 

    return render(request, 'user/company_list.html', {
        'companies': top_companies,
        'is_featured_page': True  
    })
def create_cv(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    if request.method == 'POST':
        custom_user = users.objects.get(id=user_id)
        Cvs.objects.create(
            user=custom_user,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            description=request.POST.get('description'),
            skills=request.POST.get('experience'), 
            uploaded_at=timezone.now()
        )
        messages.success(request, "Tạo hồ sơ thành công!")
        return redirect('cv_list') 

    return render(request, 'user/create_cv.html')

def cv_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    
    user_cvs = Cvs.objects.filter(user_id=user_id).order_by('-uploaded_at')
    return render(request, 'user/cv_list.html', {'cvs': user_cvs})


def matching_jobs_for_cv(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user_cvs = Cvs.objects.filter(user_id=user_id)
    
    selected_cv_id = request.GET.get('cv_id')
    recommended_jobs = []

    if selected_cv_id:
        cv = get_object_or_404(Cvs, id=selected_cv_id, user_id=user_id)
        cv_data = {
            "description": cv.description,
            "skills": cv.skills,
            "address": cv.address
        }

        all_jobs = Job.objects.all() 

        for job in all_jobs:
            percent, level, details = match_cv_fields(cv_data, job)
            
            recommended_jobs.append({
                'job': job,
                'percent': percent,
                'level': level,
                'details': details
            })

        recommended_jobs = sorted(recommended_jobs, key=lambda x: x['percent'], reverse=True)

    return render(request, 'user/matching_jobs.html', {
        'user_cvs': user_cvs,
        'recommended_jobs': recommended_jobs,
        'selected_cv_id': int(selected_cv_id) if selected_cv_id else None
    })