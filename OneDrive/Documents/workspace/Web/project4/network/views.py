import json
from django.contrib.auth import authenticate, login, logout
from django.core.files.storage import FileSystemStorage
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .forms import PostForm


from .models import Post, User


def index(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        posts = Post.objects.all().order_by('-date')
        return render(request, "network/index.html", {
            "posts":posts,
            "form":(PostForm() if request.user.is_authenticated else None),
        })

def following(request):
    current_user = get_object_or_404(User, pk=request.user.id)
    followers = current_user.following.all()
    posts = Post.objects.filter(user__in=followers).order_by('-date')
    return render(request, "network/index.html", {
        "posts":posts,
    })
    
def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    posts = Post.objects.filter(user=user).order_by('-date')

    if request.method == 'GET':
        
        return render(request, "network/profile.html", {
            "posts":posts,
            "user":user,
            "isuser":(True if request.user == user else False),
        })
    else:
        current_user = request.user
        if current_user.is_authenticated:
            if current_user in user.followers.all():
                user.followers.remove(current_user)
                current_user.following.remove(user)
            else:
                user.followers.add(current_user)
                current_user.following.add(user)
        return HttpResponseRedirect(f"/profile/{user.id}")
                
                
            



@csrf_exempt
def update_post(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        post_id = data.get('postId'); new_text = data.get('newText')
        post = Post.objects.get(pk=int(post_id))

        if request.user.id == post.user.id:
            post.text = new_text
            post.save()
            return JsonResponse({'message': 'Post updated successfully'})
        return JsonResponse({'message': 'an error happened'})

@csrf_exempt
def like_post(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        post_id = data.get('postId')
        post = Post.objects.get(pk=int(post_id))
        user = User.objects.get(pk=request.user.id)

        try:
            if not user in post.likers.all():
                post.likers.add(user)
            else:
                post.likers.remove(user)
            post.save()
            return JsonResponse({'message': 'like updated successfully'})
        except:
            return JsonResponse({'message': 'an error happened'})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == 'POST':
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
            
        if(request.FILES):
            profile_pic = request.FILES['profile_pic']
            destination = 'media/profile_pics/' 
            fs = FileSystemStorage(location=destination)
            filename = fs.save(profile_pic.name, profile_pic)
            user.image = 'profile_pics/' + filename 
        
        user.save()
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

