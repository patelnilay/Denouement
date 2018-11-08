from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from PIL import Image

from .forms import SignInForm, SignUpForm, ImageForm, PostForm, ThreadForm, CommentForm
from .models import ForumCategory, ForumThread, ForumPost, ProfileComment

import re
import urllib.request

def is_banned(user):
    for group in user.groups.all():
        if group.name  == 'Banned':
            return True

    return False

def index(request):
    #success = request.session.pop('alert', None)
    #return render(request, 'denouement/index.html', {'success': success})
    return redirect('/forums')

def obj_to_url_string(obj):
    obj.title = re.sub(' +', ' ', obj.title)
    return re.sub("[^0-9a-zA-Z-]+", "", obj.title.replace(' ', '-').lower())

def forums(request):
    categories = ForumCategory.objects.all()

    # Uhh not sure about this
    for category in categories:
        category.url = obj_to_url_string(category) #category.title.replace(' ', '-').lower()

    return render(request, 'denouement/index.html', {'categories': categories})

def delete_thread(request, thread_id):
    if not request.user.has_perm('denouement.delete_forumthread'):
        return HttpResponseForbidden("You do not have permission to delete this thread")
    
    selected_thread = get_object_or_404(ForumThread, id=thread_id)
    category_id = selected_thread.category.id
    selected_thread.delete()

    return redirect("/forums/categories/" + str(category_id))


@login_required(login_url="/forums/account/signin")
def post_thread(request, category_id):
    if is_banned(request.user):
        return HttpResponseForbidden("You are banned")

    try:
        category = ForumCategory.objects.get(id=category_id)
    except ForumCategory.DoesNotExist:
        return redirect('/forums')

    title = request.POST.get('title', None)
    text = request.POST.get('text', None)

    forms = [ThreadForm(), PostForm()]

    # TODO: Look at the Django way of not repeating something like this
    if text == None or title == None or text[0].isspace() or title[0].isspace():
        return render(request, 'denouement/forum_post_thread.html', {'forms': forms})
 
    if request.method == "POST":
        date = datetime.now()
        thread = ForumThread.objects.create(title=title, category=category, author=request.user, date=date)
        ForumPost.objects.create(text=text, author=request.user, thread=thread, date=date)
        return redirect('/forums/thread/' + str(thread.id))

    return render(request, 'denouement/forum_post_thread.html', {'forms': forms})

@login_required(login_url="/forums/account/signin")
def edit_forum_post(request, thread_id, post_id):
    if is_banned(request.user):
        return HttpResponseForbidden("You are banned")

    form = None

    try:
        thread = ForumThread.objects.get(id=thread_id)
    except ForumPost.DoesNotExist:
        return redirect('forums')

    try:
        post = ForumPost.objects.get(thread=thread, id=post_id)
    except ForumPost.DoesNotExist:
        return redirect('forums')

    # We know the post and thread exist and as such we can access the text
    # so the form has a default value
    form = PostForm(initial={'text': post.text})

    if (not request.user.has_perm('denouement.change_forumpost') and
        post.author != request.user):

        return redirect('forums')

    if request.method == "POST":   
        text = request.POST.get('text', None)

        # TODO: Look at the Django way of not repeating something like this
        if text == None or text[0].isspace():
            return render(request, 'denouement/forum_post_thread.html', {'forms': [form]})

        post.text = text
        post.save()

        return redirect('../../')

    return render(request, 'denouement/forum_post_thread.html', {'forms': [form]})

def view_untitled_objects(model_type, id):
    try: 
        obj = model_type.objects.get(id=id)
    except model_type.DoesNotExist:
        # TODO: add some error

        return redirect("/forums")
    return redirect("../" + str(id) + "/" + obj_to_url_string(obj))

def view_titled_objects(request, model_type, related_model, id, title, template_name, output_name):
    try: 
        obj = model_type.objects.get(id=id)
    except model_type.DoesNotExist:
        # TODO: add some error
        return redirect("/forums")

    # We only want alphanumeric and hyphens in URL's
    obj.title = re.sub(' +', ' ', obj.title)
    if title != re.sub("[^0-9a-zA-Z-]+", "",obj.title.replace(' ', '-').lower()):
        return redirect("../" + obj_to_url_string(obj))

    desired_objs = None
    parent_name = None
    form = None
    post_url = None

    if model_type._meta.object_name == "ForumThread":
        desired_objs = related_model.objects.filter(thread=obj)
        parent_name = obj.title
        form = PostForm()
    elif model_type._meta.object_name == "ForumCategory":
        desired_objs = {}
        desired_objs['threads'] = related_model.objects.filter(category=obj, pinned=False).order_by('-date')
        desired_objs['pinned_threads'] = related_model.objects.filter(pinned=True).order_by('-date')

        parent_name = obj.title
        post_url = "/forums/post/" + str(obj.id)

    # TODO: Maybe raise an error incase i'm doing something dumb with the wrong model?

    return render(request, 'denouement/' + template_name + '.html', {output_name: desired_objs, 'parent': obj, 'post_url': post_url, 'form': form})
    
def view_forum_category_untitled(request, id):
    return view_untitled_objects(ForumCategory, id)

def view_forum_category(request, id, title):
    return view_titled_objects(request, ForumCategory, ForumThread, id, title, 'forum_category', 'threads')

def view_forum_thread_untitled(request, id):
    return view_untitled_objects(ForumThread, id)

def view_forum_thread(request, id, title):
    # Probably tell the user they don't have permission
    if request.method == "POST" and request.user.is_authenticated:

        if is_banned(request.user):
            return HttpResponseForbidden("You are banned")

        thread = ForumThread.objects.get(id=id)

        if thread.locked:
            return HttpResponseForbidden("This thread is locked")

        text = request.POST.get('text', None)
        ForumPost.objects.create(text=text, author=request.user, thread=thread, date=datetime.now())

    return view_titled_objects(request, ForumThread, ForumPost, id, title, 'forum_thread', 'posts')

@login_required(login_url="/forums/account/signin")
def delete_forum_post(request, thread_id, post_id):
    if is_banned(request.user):
        return HttpResponseForbidden("You are banned")

    if not request.user.has_perm("denouement.delete_forumpost"):
        return HttpResponseForbidden("You cannot delete this thread")

    if request.user.has_perm('denouement.delete_forumpost'):
        thread = get_object_or_404(ForumThread, id=thread_id)
        post = get_object_or_404(ForumPost, id=post_id, thread=thread)
        post.delete()
        return redirect("../../")
    else:
        return HttpResponseForbidden("You do not have the permissions to delete this")

@login_required(login_url="/forums/account/signin")
def lock_thread(request, thread_id):
    if not request.user.has_perm("denouement.lock_forumthread"):
        return HttpResponseForbidden("You cannot lock this thread")

    selected_thread = get_object_or_404(ForumThread, id=thread_id)
    selected_thread.locked = not selected_thread.locked
    selected_thread.save()
    return redirect('../')   

@login_required(login_url="/forums/account/signin")
def pin_thread(request, thread_id):
    if not request.user.has_perm("denouement.pin_forumthread"):
        return HttpResponseForbidden("You cannot pin this thread")

    selected_thread = get_object_or_404(ForumThread, id=thread_id)
    selected_thread.pinned = not selected_thread.pinned
    selected_thread.save()
    return redirect('../') 

@login_required(login_url="/forums/account/signin")
def delete_profile_comment(request, username, comment_id):
    if is_banned(request.user):
        return HttpResponseForbidden("You are banned")

    user = get_object_or_404(User, username=username)

    if request.user == user:
        comment = get_object_or_404(ProfileComment, id=comment_id, profile_owner=user)
        comment.delete()
        return redirect("../../../")
    else:
        return HttpResponseForbidden("You do not have the permissions to delete this")

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

        if not username.isalnum():
            return render(request, 'denouement/sign_up.html', {'form': form, 'error': 'Your username should only consist of numbers and letters'})

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
            user = User.objects.create_user(username=username, password=password, email=email)
            default_user_group = Group.objects.get(name='User')
            default_user_group.user_set.add(user)

            alert = 'Congratulations, you registered an account!'
            request.session['alert'] = alert

            urllib.request.urlretrieve('https://api.adorable.io/avatars/285/'+ user.username + '.png', 'media/' + user.username + '.jpg')

            return redirect('/')
    return render(request, 'denouement/sign_up.html', {'form': form})

def sign_out(request):
    logout(request)
    request.session['alert'] = 'You\'ve successfully logged out'
    return redirect('/')   

def view_user_profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('/forums')

    comment_form = CommentForm()

    # We set this later on if the user should be editing the profile of the selected user
    image_form = None
    
    if user == request.user:    
        image_form = ImageForm()

    comments = ProfileComment.objects.filter(profile_owner=user)

    # TODO: Look at not doing this
    img_url = '/media/' + user.username + '.jpg'

    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('text', None)

        if text and user.is_authenticated:
            comment = ProfileComment.objects.create(text=text, author=request.user, profile_owner=user, date=datetime.now())
            comment.save()

    if is_banned(user):
        user.banned = True

    return render(request, 'denouement/account.html', {'img_url': img_url, 'selected_user': user, 
        'forms': {'comment_form': comment_form, 'image_form': image_form}, 'comments': comments})

@login_required(login_url="/forums/account/signin")
def user_moderation(request, username, action):
    # Strip banned users of staff ranks?
    if is_banned(request.user):
        return HttpResponseForbidden("You are banned")

    is_admin = False

    for group in request.user.groups.all():
        if group.name.lower() == 'admin':
            is_admin = True
            break

    if not is_admin:
        return HttpResponseForbidden("You do not have the permissions required to perform user moderation")

    targeted_user = get_object_or_404(User, username__iexact=username)

    banned_user_group = Group.objects.get(name='Banned')
    
    if action == 'ban':
        banned_user_group.user_set.add(targeted_user)
    elif action == 'unban':
        banned_user_group.user_set.remove(targeted_user)
    else:
        return HttpResponseForbidden()

    return redirect("../" + targeted_user.username)

@require_http_methods(['POST'])
@login_required(login_url="/forums/account/signin")
def upload_image(request):
    # we're going to need to look at security
    # file type
    # file size
    # (a lot of stuff will be done by a production web server i.e Apache and it's URL specific upload sizes etc)
    # more stuff...
    if is_banned(request.user):
        return HttpResponseForbidden("You are banned")

    if not request.FILES:
        return redirect("/forums/user/" + request.user.username)

    try:
        img = Image.open(request.FILES['image'])
    except OSError:
        request.session['alert'] = 'Invalid filetype!'
        return redirect('/forums/user/' + request.user.username)

    try:
        img.verify()
        request.session['alert'] = 'Image uploaded!'
    except Exception:
        request.session['alert'] = 'Invalid image!'
        return redirect('/forums/user/' + request.user.username)

    with open('media/' + request.user.username + '.jpg', 'wb+') as destination:
        for chunk in request.FILES['image'].chunks():
            destination.write(chunk)

    return redirect('/forums/user/' + request.user.username)