import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from frontend.forms import UserLoginForm, UserCreateForm, UpdatePostForm, CreatePostForm
from frontend.utils import format_chats

API_URL = "http://127.0.0.1:8000/api/"


def sign_up(request):
    form = UserCreateForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data
        response = requests.post(
            url=f"{API_URL}auth/users/create/",
            data=data
        )
        if response.status_code == 201:
            return redirect('login')
        else:
            pass
    return render(request, 'frontend/auth/sign_up.html', {'form': form})


def login_view(request):
    form = UserLoginForm(request.POST or None)

    if form.is_valid():
        data = form.cleaned_data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        login(request, user)

        return redirect('home')

    return render(request, 'frontend/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required()
def posts(request):
    posts_list = []
    response = requests.get(
        url=f"{API_URL}posts/",
        cookies=request.COOKIES
    )
    if response.status_code == 200:
        posts_list = response.json()
    return render(request, 'frontend/posts/posts.html', {'posts': posts_list})


def post_detail(request, pk, method):
    post = []
    post_detail_url = f"{API_URL}posts/{pk}/"
    context = {
        'posts': post,
        'is_detail': True,
        'method': method
    }
    if method == 'update':
        form = UpdatePostForm(request.POST or None)
        context['form'] = form
        if form.is_valid():
            data = form.cleaned_data
            csrf_token = request.COOKIES.get('csrftoken', None)
            response = requests.put(
                url=post_detail_url,
                data=data,
                cookies=request.COOKIES,
                headers={"X-CSRFToken": csrf_token}
            )
            if response.status_code == 200:
                return redirect('post_detail', pk=pk, method="")
            elif response.status_code == 404:
                raise Http404()
    elif method == 'delete':
        csrf_token = request.COOKIES.get('csrftoken', None)
        response = requests.delete(
            url=post_detail_url,
            cookies=request.COOKIES,
            headers={"X-CSRFToken": csrf_token}
        )
        if response.status_code == 204:
            return redirect('posts')
        elif response.status_code == 404:
            raise Http404()
    else:
        response = requests.get(
            url=post_detail_url,
            cookies=request.COOKIES
        )
        if response.status_code == 200:
            post.append(response.json())
        elif response.status_code == 404:
            raise Http404()

    return render(request, 'frontend/posts/posts.html', context)


def post_create(request):
    form = None
    response = requests.get(
        url=f"{API_URL}chats/",
        cookies=request.COOKIES
    )
    if response.status_code == 200:
        chats = format_chats(response.json())
        form = CreatePostForm(data=request.POST, files=request.FILES, chats=chats)

        if form.is_valid():
            data = form.cleaned_data.copy()
            csrf_token = request.COOKIES.get("csrftoken")
            data.pop('photo')
            data.pop('video')

            post_response = requests.post(
                url=f"{API_URL}posts/",
                data=data,
                files=request.FILES,
                cookies=request.COOKIES,
                headers={"X-CSRFToken": csrf_token}
            )
            if post_response.status_code == 201:
                return redirect('posts')

        elif request.method == 'GET':
            form = CreatePostForm(chats=chats)

    return render(request, 'frontend/posts/create_post.html', {"form": form})


@login_required
def home(request):
    return render(request, 'frontend/home.html')
