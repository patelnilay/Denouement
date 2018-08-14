from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from PIL import Image

from .forms import SignInForm, SignUpForm, ImageForm
from .models import ProfilePicture, ForumCategory, ForumThread

def index(request):
    success = request.session.pop('alert', None)
    return render(request, 'denouement/index.html', {'success': success})

def forums(request):
    categories = ForumCategory.objects.all()

    # Uhh not sure about this
    for category in categories:
        category.url = category.title.replace(' ', '-').lower()

    return render(request, 'denouement/forums_index.html', {'categories': categories})

# This get's called when the title isn't specified and redirects to a URL with the title
# TODO: This could probably be better and it should be clearer this leads to view_forum_category
def view_forum_category_untitled(request, id):
    try: 
        category = ForumCategory.objects.get(id=id)
    except ForumCategory.DoesNotExist:
        # TODO: add some error
        return redirect("/forums")
    return redirect(str(category.id) + "/" + category.title.replace(' ', '-').lower())

# NOTE: Title is cosmetic and doesn't even matter, this will always be corrected
def view_forum_category(request, id, title):
    try: 
        category = ForumCategory.objects.get(id=id)
    except ForumCategory.DoesNotExist:
        # TODO: add some error
        return redirect("/forums")

    # For that wise guy who didn't copy and paste right
    # TODO: Unshitify?
    if title.replace('-', ' ').lower() != category.title.lower():
        # Needed the initial / to stop Django thinking it was a reverse thing, research this?
        return redirect("../" + str(category.id) + "/" + str(category.title.replace(' ', '-').lower()))

    threads = ForumThread.objects.filter(category=category)

    return render(request, 'denouement/forum_category.html', {'threads': threads, 'category_title': category.title})



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

def view_account(request):
    alert = request.session.pop('alert', None)
    form = ImageForm()
    img_url = '/media/' + request.user.username + '.jpg'
    return render(request, 'denouement/account.html', {'form': form, 'img_url': img_url, 'alert': alert})

@require_http_methods(['POST'])
@login_required
def upload_image(request):
    # we're going to need to look at security
    # file type
    # file size
    # (a lot of stuff will be done by a production web server i.e Apache and it's URL specific upload sizes etc)
    # more stuff...
    try:
        img = Image.open(request.FILES['image'])
    except OSError:
        request.session['alert'] = 'Invalid filetype!'
        return redirect('../account')

    try:
        img.verify()
        request.session['alert'] = 'Image uploaded!'
    except Exception:
        request.session['alert'] = 'Invalid image!'
        return redirect('../account')

    with open('media/' + request.user.username + '.jpg', 'wb+') as destination:
        for chunk in request.FILES['image'].chunks():
            destination.write(chunk)

    return redirect('../account')
