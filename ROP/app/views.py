from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse

# Create your views here.
#admin
def homeAdmin(request):
    return render(request, 'admin/home.html')

def post_detail(request):
    return render(request, 'admin/post_detail.html')

def ListJob(request):
    return render(request, 'admin/ListJob.html')


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





