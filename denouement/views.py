from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from PIL import Image

from .forms import SignInForm, SignUpForm, ImageForm
from .models import ProfilePicture, ForumCategory, ForumThread, ForumPost

def index(request):
    success = request.session.pop('alert', None)
    return render(request, 'denouement/index.html', {'success': success})

def obj_to_url_string(obj):
    return obj.title.replace(' ', '-').lower()

def forums(request):
    categories = ForumCategory.objects.all()

    # Uhh not sure about this
    for category in categories:
        category.url = obj_to_url_string(category) #category.title.replace(' ', '-').lower()

    return render(request, 'denouement/forums_index.html', {'categories': categories})

def view_untitled_objects(model_type, id):
    try: 
        obj = model_type.objects.get(id=id)
    except ForumCategory.DoesNotExist:
        # TODO: add some error
        return redirect("/forums")
    return redirect(str(obj.id) + "/" + obj_to_url_string(obj))

def view_titled_objects(request, model_type, related_model, id, title, template_name, output_name):
    try: 
        obj = model_type.objects.get(id=id)
    except ForumCategory.DoesNotExist:
        # TODO: add some error
        return redirect("/forums")

    # For that wise guy who didn't copy and paste right
    if title.replace('-', ' ').lower() != obj.title.lower():
        return redirect("../" + str(obj.id) + "/" + obj_to_url_string(obj))

    desired_objs = None
    parent_name = None

    if model_type._meta.object_name == "ForumThread":
        desired_objs = related_model.objects.filter(thread=obj)
        parent_name = obj.title
    elif model_type._meta.object_name == "ForumCategory":
        desired_objs = related_model.objects.filter(category=obj)
        parent_name = obj.title

    # TODO: Maybe raise an error incase i'm doing something dumb with the wrong model?

    return render(request, 'denouement/' + template_name + '.html', {output_name: desired_objs, 'parent_name': parent_name})
    
def view_forum_category_untitled(request, id):
    return view_untitled_objects(ForumCategory, id)

def view_forum_category(request, id, title):
    return view_titled_objects(request, ForumCategory, ForumThread, id, title, 'forum_category', 'threads')

def view_forum_thread_untitled(request, id):
    return view_untitled_objects(ForumCategory, id)

def view_forum_thread(request, id, title):
    return view_titled_objects(request, ForumThread, ForumPost, id, title, 'forum_thread', 'posts')

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
