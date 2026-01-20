from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.template.defaultfilters import title
from django.db.models import Q
from .decorator import user_required, employer_required
from .AI.cv_matcher import match_cv_fields
# from .AI.cv_matcher import  match_cv_with_job
from django.core.exceptions import ValidationError
# from .AI.cv_matcher import extract_cv_text, match_cv_with_job, match_cv_fields
from .models import Applications, Job, Cvs
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST

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


@employer_required
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


@employer_required
def ListJob(request):
    user_id = request.session.get('user_id')
    if request.method == 'GET':
        if not user_id:
            return redirect('login')
    jobs = Job.objects.all().filter(user=user_id).order_by("-create_at")
    # jobs = Job.objects.all()
    return render(request, 'admin/ListJob.html', {'jobs': jobs})


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
def is_strong_password(password):
    """
    Ít nhất 8 ký tự
    Có ít nhất 1 chữ viết hoa
    Có ít nhất 1 ký tự đặc biệt
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=/\\[\]]', password):
        return False
    return True

# login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password

def login(request):
    if 'user_id' in request.session:
        if request.session.get('user_role'):
            return redirect('ListJob')
        return redirect('home')

    context = {}

    # ================= ĐĂNG KÝ =================
    if request.method == 'POST' and 'full_name' in request.POST:
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        selected_role = request.POST.get('role', 'candidate')

        is_admin = True if selected_role == 'employer' else False
        context['show_register'] = True  # ⭐ giữ tab đăng ký

        if not all([full_name, email, phone, password, confirm_password]):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.", extra_tags="register")
            return render(request, 'login/login.html', context)

        if password != confirm_password:
            messages.error(request, "Mật khẩu và xác nhận mật khẩu không khớp.", extra_tags="register")
            return render(request, 'login/login.html', context)

        if not is_strong_password(password):
            messages.error(
                request,
                "Mật khẩu phải có ít nhất 8 ký tự, 1 chữ viết hoa và 1 ký tự đặc biệt.",
                extra_tags="register"
            )
            return render(request, 'login/login.html', context)

        try:
            users.objects.create(
                fullname=full_name,
                email=email,
                phone=phone,
                password_hash=make_password(password),
                role=is_admin
            )
            messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.", extra_tags="login")
            return redirect('login')

        except IntegrityError:
            messages.error(request, "Email hoặc số điện thoại đã tồn tại.", extra_tags="register")
            return render(request, 'login/login.html', context)

        except Exception:
            messages.error(request, "Có lỗi xảy ra, vui lòng thử lại.", extra_tags="register")
            return render(request, 'login/login.html', context)

    # ================= ĐĂNG NHẬP =================
    elif request.method == 'POST' and 'email_login' in request.POST:
        email = request.POST.get('email_login', '').strip()
        password = request.POST.get('password_login', '').strip()

        try:
            user = users.objects.get(email=email)
        except users.DoesNotExist:
            messages.error(request, "Email hoặc mật khẩu không đúng.", extra_tags="login")
            return render(request, 'login/login.html')

        if not check_password(password, user.password_hash):
            messages.error(request, "Email hoặc mật khẩu không đúng.", extra_tags="login")
            return render(request, 'login/login.html')

        request.session['user_id'] = user.id
        request.session['user_full_name'] = user.fullname
        request.session['user_role'] = user.role
        request.session['user_email'] = user.email

        if user.email == "admin@gmail.com":
            return redirect('admin_manage_candidates')
        elif user.role:
            return redirect('ListJob')
        return redirect('home')

    return render(request, 'login/login.html')

# def login(request):
#     if 'user_id' in request.session:
#         user_role = request.session.get('user_role')
#         if user_role:
#             return redirect('ListJob')
#         else:
#             return redirect('home')
#
#     # ====== ĐĂNG KÝ ======
#     if request.method == 'POST' and 'full_name' in request.POST:
#         full_name = request.POST.get('full_name', '').strip()
#         email = request.POST.get('email', '').strip()
#         phone = request.POST.get('phone', '').strip()
#         password = request.POST.get('password', '').strip()
#         confirm_password = request.POST.get('confirm_password', '').strip()
#         selected_role = request.POST.get('role', 'candidate')
#
#         is_admin = True if selected_role == 'employer' else False
#
#         if not full_name or not email or not phone or not password or not confirm_password:
#             messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
#             return render(request, 'login/login.html')
#
#         if password != confirm_password:
#             messages.error(request, "Mật khẩu và xác nhận mật khẩu không khớp!")
#             return render(request, 'login/login.html')
#
#         # 🔐 KIỂM TRA ĐỘ MẠNH MẬT KHẨU
#         if not is_strong_password(password):
#             messages.error(
#                 request,
#                 "Mật khẩu phải có ít nhất 8 ký tự, 1 chữ viết hoa và 1 ký tự đặc biệt."
#             )
#             return render(request, 'login/login.html')
#
#         hashed_password = make_password(password)
#
#         try:
#             users.objects.create(
#                 fullname=full_name,
#                 email=email,
#                 phone=phone,
#                 password_hash=hashed_password,
#                 role=is_admin
#             )
#             messages.success(request, "Đăng ký thành công! Vui lòng đăng nhập.")
#             return redirect('login')
#
#         except IntegrityError:
#             messages.error(request, "Email hoặc Số điện thoại đã tồn tại. Vui lòng thử lại.")
#             return render(request, 'login/login.html')
#
#         except Exception as e:
#             messages.error(request, "Đã có lỗi xảy ra trong quá trình đăng ký.")
#             return render(request, 'login/login.html')
#
#     # ====== ĐĂNG NHẬP ======
#     elif request.method == 'POST' and 'email_login' in request.POST:
#         email = request.POST.get('email_login')
#         password = request.POST.get('password_login')
#
#         try:
#             user = users.objects.get(email=email)
#         except users.DoesNotExist:
#             messages.error(request, "Email hoặc mật khẩu không đúng.")
#             return render(request, 'login/login.html')
#
#         if check_password(password, user.password_hash):
#             request.session['user_id'] = user.id
#             request.session['user_full_name'] = user.fullname
#             request.session['user_role'] = user.role
#             request.session['user_email'] = user.email
#
#             if user.email == "admin@gmail.com":
#                 return redirect('admin_manage_candidates')
#             elif user.role:
#                 return redirect('ListJob')
#             else:
#                 return redirect('home')
#         else:
#             messages.error(request, "Email hoặc mật khẩu không đúng.")
#             return render(request, 'login/login.html')
#
#     return render(request, 'login/login.html')



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


import re
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render, redirect



@user_required
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

        # 🔐 KIỂM TRA ĐỘ MẠNH MẬT KHẨU
        if not is_strong_password(new_password):
            messages.error(
                request,
                "Mật khẩu phải có ít nhất 8 ký tự, 1 chữ viết hoa và 1 ký tự đặc biệt."
            )
            return render(request, 'user/ChangePassword.html')

        user.password_hash = make_password(new_password)
        user.save(update_fields=['password_hash'])

        messages.success(request, "Đổi mật khẩu thành công!")
        return redirect('home')

    return render(request, 'user/ChangePassword.html')

@user_required
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


@user_required
def appliedJobsList(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    return render(request, 'user/appliedJobsList.html')


# cái này db
@employer_required
def functionPost(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')

    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_obj = get_object_or_404(users, id=user_id)

        try:
            job = Job(
                title=request.POST.get('title'),
                company=request.POST.get('company_name'),
                location=request.POST.get('location'),
                salary_min=int(request.POST.get('salary_min')) if request.POST.get('salary_min') else None,
                salary_max=int(request.POST.get('salary_max')) if request.POST.get('salary_max') else None,
                description=request.POST.get('description'),
                requirements=request.POST.get('requirements'),
                benefit=request.POST.get('benefits'),
                skills=request.POST.get('skills'),
                end_date=request.POST.get('end_date'),
                category=classify_job_category(
                    request.POST.get('title'),
                    request.POST.get('skills'),
                    request.POST.get('description')
                ),
                user=user_obj
            )

            # 🔥🔥🔥 DÒNG QUAN TRỌNG NHẤT
            job.full_clean()  # CHẠY TOÀN BỘ LUẬT CHỐNG SPAM

            job.save()

            messages.success(request, 'Đăng tin tuyển dụng thành công!')
            return redirect('ListJob')

        except ValidationError as e:
            messages.error(request, e.message if hasattr(e, 'message') else e.messages[0])
            return render(request, 'admin/functionPost.html')

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
@user_required
def appliedJobsList(request):
    custom_user = users.objects.get(id=request.session['user_id'])

    applications = Applications.objects.filter(user=custom_user).select_related('job').order_by('-applied_at')

    return render(request, 'user/appliedJobsList.html', {'applications': applications})


@employer_required
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

from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
import json
@require_POST
def reject_application(request, app_id):
    # 🔒 Chỉ cho AJAX
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    application = get_object_or_404(Applications, id=app_id)

    if application.status != 'new':
        return JsonResponse({'status': 'error', 'message': 'Hồ sơ đã được xử lý'})

    try:
        data = json.loads(request.body)
        note = data.get('note', '')
    except:
        note = ''

    # ✅ CẬP NHẬT DB
    application.status = 'rejected'
    application.is_rejected = True
    application.is_sent = False
    application.employer_note = note
    application.save()

    return JsonResponse({'status': 'success'})
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.mail import send_mail

@require_POST
def send_interview_email(request, app_id):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    application = get_object_or_404(Applications, id=app_id)

    if application.status != 'new':
        return JsonResponse({'status': 'error', 'message': 'Hồ sơ đã được xử lý'}, status=400)

    cv = application.cv
    job = application.job

    try:
        data = json.loads(request.body)
    except:
        data = {}

    itv_time = data.get('time', 'Sẽ thông báo sau')
    itv_location = data.get('location', 'Tại văn phòng công ty')
    itv_docs = data.get('docs', 'Không yêu cầu')
    itv_contact = data.get('contact', 'Phòng nhân sự')

    subject = f"[Mời phỏng vấn] Vị trí {job.title}"

    message = f"""
Chào {cv.full_name},

Chúng tôi đã xem xét hồ sơ của bạn cho vị trí {job.title}.
Chúng tôi trân trọng mời bạn tham gia buổi phỏng vấn.

CHI TIẾT BUỔI PHỎNG VẤN:
- Thời gian: {itv_time}
- Địa điểm: {itv_location}
- Tài liệu cần chuẩn bị: {itv_docs}
- Liên hệ: {itv_contact}

Vui lòng phản hồi email này để xác nhận tham gia.

Trân trọng,
Phòng nhân sự {job.company}
"""

    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [cv.email],   # ✅ EMAIL TRONG HỒ SƠ
            fail_silently=False
        )
    except:
        return JsonResponse({'status': 'error', 'message': 'Gửi email thất bại'}, status=500)

    application.status = 'passed'
    application.is_sent = True
    application.save()

    return JsonResponse({'status': 'success'})


@employer_required
def cv_detail_form(request, cv_id):
    cv = get_object_or_404(Cvs, id=cv_id)
    return render(request, 'admin/detail.html', {'cv': cv})


@user_required
def cv_detail_form_user(request, cv_id):
    cv = get_object_or_404(Cvs, id=cv_id)
    return render(request, 'user/detail.html', {'cv': cv})


# them
@user_required
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


@user_required
def home_view(request):
    jobs = Job.objects.all().order_by('-create_at')[:10]
    return render(request, 'home.html', {'jobs': jobs})


@user_required
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

    categories = Job.objects.exclude(category__isnull=True).exclude(category='').values_list('category',
                                                                                             flat=True).distinct()

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


@user_required
def company_list(request):
    all_companies = Job.objects.exclude(company__isnull=True).exclude(company='') \
        .values('company') \
        .annotate(num_jobs=Count('id')) \
        .order_by('company')  # Sắp xếp A-Z

    return render(request, 'user/company_list.html', {
        'companies': all_companies
    })


@user_required
def featured_companies(request):
    top_companies = Job.objects.exclude(company__isnull=True).exclude(company='') \
        .values('company') \
        .annotate(num_jobs=Count('id')) \
        .order_by('-num_jobs')

    return render(request, 'user/company_list.html', {
        'companies': top_companies,
        'is_featured_page': True
    })


@user_required
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


from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa
from .models import Applications
from xhtml2pdf import pisa

from xhtml2pdf import pisa


# @employer_required
# def application_pdf_download(request, app_id):
#     application = get_object_or_404(Applications, id=app_id)
#     template = get_template("admin/cv_pdf.html")
#     html = template.render({"application": application})
#
#     response = HttpResponse(content_type="application/pdf")
#     response["Content-Disposition"] = f'attachment; filename="application_{app_id}.pdf"'
#
#     pisa.DEFAULT_FONT = "DejaVuSans"  # 🔥 BẮT BUỘC
#     pisa.CreatePDF(html, dest=response, encoding="UTF-8")
#
#     return response


def test_font(request):
    return render(request, "test_font.html")


from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def test_pdf_font(request):
    template = get_template("test_pdf.html")
    html = template.render({})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=test.pdf"

    pisa.DEFAULT_FONT = "DejaVuSans"

    pisa.CreatePDF(
        html,
        dest=response,
        encoding="UTF-8"
    )
    return response


from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import get_object_or_404
from .models import Applications  # nhớ import model


@employer_required
def application_pdf_download(request, app_id):
    application = get_object_or_404(Applications, id=app_id)

    html_string = render_to_string(
        "admin/application_detail.html",
        {"application": application}
    )

    pdf_file = HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/")
    ).write_pdf()  # trả về bytes

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=application_{app_id}.pdf'
    return response


def cv_pdf_download(request, cv_id):
    cv = get_object_or_404(Cvs, id=cv_id)

    html_string = render_to_string(
        "user/cv_pdf.html",
        {
            "cv": cv
        }
    )

    pdf_file = HTML(
        string=html_string,
        base_url=request.build_absolute_uri("/")
    ).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=cv_{cv_id}.pdf'
    return response


# KIEU
@user_required
def detailPost(request, id):
    user_id = request.session.get('user_id')

    job = get_object_or_404(Job, id=id)

    user_cvs = Cvs.objects.filter(user_id=user_id)
    has_cv = user_cvs.exists()

    # 🔴 CHECK ĐÃ ỨNG TUYỂN CHƯA
    has_applied = Applications.objects.filter(
        job_id=id,
        user_id=user_id
    ).exists()

    today = timezone.now().date()
    is_active = job.create_at <= today <= job.end_date

    context = {
        'job': job,
        'user_cvs': user_cvs,
        'has_cv': has_cv,
        'has_applied': has_applied,  # ✅ QUAN TRỌNG
        'jobDescript': split_text(job.description),
        'jobRequire': split_text(job.requirements),
        'jobSkill': split_text(job.skills),
        'jobBenefit': split_text(job.benefit),
        'is_active': is_active,
    }

    return render(request, 'user/detailPost.html', context)

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone

@user_required
def apply_job(request, job_id):
    if request.method != 'POST':
        return redirect('home')

    user_id = request.session.get('user_id')

    # 🔴 Đã apply job này chưa
    if Applications.objects.filter(job_id=job_id, user_id=user_id).exists():
        messages.warning(request, "Bạn đã ứng tuyển công việc này rồi!")
        return redirect('detailPost', id=job_id)

    # 🔹 Lấy CV hiện có (nếu có)
    cv = Cvs.objects.filter(user_id=user_id).first()

    # ==================================================
    # 🔥 CHƯA CÓ CV → TẠO GIỐNG create_cv
    # ==================================================
    if not cv:
        custom_user = users.objects.get(id=user_id)

        cv = Cvs.objects.create(
            user=custom_user,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            description=request.POST.get('description'),
            skills=request.POST.get('experience'),
            uploaded_at=timezone.now()
        )

    # ==================================================
    # ✅ TẠO APPLICATION
    # ==================================================
    Applications.objects.create(
        job_id=job_id,
        cv=cv,
        user_id=user_id,
        applied_at=timezone.now(),
        status='new'
    )

    messages.success(request, "Ứng tuyển thành công! Hồ sơ đã được lưu.")
    return redirect('appliedJobsList')

# KIEU
@user_required
def create_cv(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    existing_cv = Cvs.objects.filter(user_id=user_id).first()

    if request.method == 'POST':
        # 🔴 Nếu đã có CV → báo lỗi & render lại
        if existing_cv:
            messages.error(request, "Bạn đã có hồ sơ trên hệ thống!")
            return render(request, 'user/create_cv.html', {
                'existing_cv': existing_cv
            })

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
        return redirect('cv_list')  # ✅ ĐÚNG

    # GET request
    return render(request, 'user/create_cv.html', {
        'existing_cv': existing_cv
    })


@user_required
def cv_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    cv = Cvs.objects.filter(user_id=user_id).first()

    # ===== CHƯA CÓ CV =====
    if not cv:
        return render(request, 'user/cv_list.html', {
            'cv': None
        })

    # ===== CÓ CV → UPDATE =====
    if request.method == 'POST':
        cv.full_name = request.POST.get('full_name')
        cv.phone = request.POST.get('phone')
        cv.address = request.POST.get('address')
        cv.description = request.POST.get('description')
        cv.skills = request.POST.get('experience')
        cv.save()

        messages.success(request, "Cập nhật hồ sơ thành công!")
        return redirect('cv_list')

    return render(request, 'user/cv_list.html', {
        'cv': cv
    })


# cái này update thêm cho AI
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


@require_POST
def update_job_and_reanalyze(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Chỉ admin hoặc chủ job mới được chỉnh (tùy logic của bạn)
    if not request.user.is_authenticated:  # hoặc kiểm tra role/admin
        return JsonResponse({'status': 'error', 'message': 'Không có quyền'}, status=403)

    try:
        # Lấy dữ liệu từ form
        job.description = request.POST.get('description', job.description).strip()
        job.requirements = request.POST.get('requirements', job.requirements).strip()
        job.skills = request.POST.get('skills', job.skills).strip()

        job.save(update_fields=['description', 'requirements', 'skills'])

        # Tính lại điểm cho tất cả applications của job này
        analyze_cvs_for_job(job)  # hàm bạn đã có sẵn

        # Optional: lấy lại danh sách mới để trả về (nếu muốn cập nhật giao diện realtime)
        updated_analyses = analyze_cvs_for_job(job)  # gọi lại để lấy data mới

        return JsonResponse({
            'status': 'success',
            'message': 'Đã cập nhật JD và tính lại điểm AI cho tất cả ứng viên!',
            # Nếu muốn trả data mới để update giao diện mà không reload
            # 'analyses': [...]  (tùy chọn)
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Có lỗi xảy ra: {str(e)}'
        }, status=500)


@require_POST
@employer_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if Applications.objects.filter(job=job).exists():
        messages.error(request, "Không thể xóa bài đăng vì đã có ứng viên.")
        return redirect('ListJob')

    job.delete()
    messages.success(request, "Đã xóa bài đăng thành công!")
    return redirect('ListJob')