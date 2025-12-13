from django.contrib import messages
from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import *


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

    return render(request, 'admin/ListJob.html')
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    jobs = Job.objects.all()
    return render(request, 'admin/ListJob.html', {'jobs': jobs})


def manaPostCV(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    return render(request, 'admin/managePostCV.html')



# login
def login(request):

    return render(request, 'login/login.html')


# user
def homeUser(request):
    # if request.method == 'GET':
    #     user_id = request.session.get('user_id')
    #     if not user_id:
    #         return redirect('login')
    jobs = Job.objects.all().order_by('-create_at')
    return render(request, 'user/home.html', {'jobs': jobs})


def ChangePassword(request):
    return render(request, 'user/ChangePassword.html')


def detailPost(request):
    if request.method == 'GET':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
    return render(request, 'user/detailPost.html')

def personalprofile(request):
    return render(request, 'user/personalprofile.html')
def appliedJobsList(request):
    return render(request, 'user/appliedJobsList.html')

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


def functionPost(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('login')
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

