from django.shortcuts import redirect
from django.contrib import messages

def employer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')

        if not request.session.get('user_role'):  # False = user
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return wrapper


def user_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')

        if request.session.get('user_role'):  # True = employer
            return redirect('ListJob')

        return view_func(request, *args, **kwargs)
    return wrapper