from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .forms import SignInForm, SignUpForm

def index(request):
    success = request.session.pop('alert', None)
    return render(request, 'denouement/index.html', {'success': success})

def sign_in(request):
    if request.user.is_authenticated:
        return redirect('/account')

    form = SignInForm()

    if request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)

        # Get correct case for username
        try:
            username = User.objects.get(username__iexact=username).username
        except User.DoesNotExist:
            pass

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/")

        error = 'Invalid credentials'
        return render(request, 'denouement/sign_in.html', {'form': form, 'error': error})

    return render(request, 'denouement/sign_in.html', {'form': form})

def sign_up(request):
    if request.user.is_authenticated:
        return redirect('/account')

    form = SignUpForm()

    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        email = request.POST.get('email', None)

        if not username or not password or not email:
            return render(request, 'denouement/sign_up.html', {'form': form, 'error': "Error"})
        
        # Maybe make this into an array and serve an array of errors 
        error = None

        try:
            if User.objects.get(username__iexact=username):
                error = 'Username in use'
        except User.DoesNotExist:
            pass

        try:
            if User.objects.get(email__iexact=email):
                error = 'Email in use'
        except User.DoesNotExist:
            pass

        if error:
            return render(request, 'denouement/sign_up.html', {'form': form, 'error': error})
        else:
            User.objects.create_user(username=username, password=password, email=email)
            
            alert = 'Congratulations, you registered an account!'
            request.session['alert'] = alert

            return redirect('/')
    return render(request, 'denouement/sign_up.html', {'form': form})

def sign_out(request):
    logout(request)
    request.session['alert'] = 'You\'ve successfully logged out'
    return redirect('/')