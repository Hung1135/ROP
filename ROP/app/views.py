from django.shortcuts import render, reverse
from django.shortcuts import redirect
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, 'admin/home.html')

def home(request):
    return render(request,'user/home.html')
def detailPost(request):
    return render(request,'user/detailPost.html')