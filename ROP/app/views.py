from django.contrib import messages
from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse
from .models import *

# Create your views here.
#admin
def homeAdmin(request):
    return render(request, 'admin/home.html')


def post_detail(request, job_id):
    job = Job.objects.get(id=job_id)
    return render(request, 'admin/post_detail.html', {'job': job})

def ListJob(request):
    jobs = Job.objects.all()
    return render(request, 'admin/ListJob.html', {'jobs': jobs})

def manaPostCV(request):
    return render(request, 'admin/managePostCV.html')


#login
def login(request):
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



# cái này db
def functionPost(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        company_name = request.POST.get('company_name')  # bạn ghi trong form là company_name
        location = request.POST.get('location')
        salary_min = request.POST.get('salary_min')
        salary_max = request.POST.get('salary_max')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        benefit = request.POST.get('benefits')
        Job.objects.create(
            title=title,
            company=company_name,
            location=location,
            salary_min=int(salary_min) if salary_min else None,
            salary_max=int(salary_max) if salary_max else None,
            description=description,
            requirements=requirements,
            benefit=benefit,
        )
        messages.success(request, 'Đăng tin tuyển dụng thành công!')
        return redirect('ListJob')
    return render(request, 'admin/functionPost.html')







