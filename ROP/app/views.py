from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
#admin
def filter(request):
    return render(request, 'admin/ad_filter.html')

def post_detail(request):
    return render(request, 'admin/post_detail.html')

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