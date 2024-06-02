import requests
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.backends.db import SessionStore
from django.core.handlers.wsgi import WSGIRequest
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect

from frontend.forms import UserLoginForm, UserCreateForm, UpdatePostForm, CreatePostForm, CreateInstagramAccountForm, \
    CreateTelegramAccountForm
from frontend.utils import format_chats

API_URL = "http://127.0.0.1:8000/api/"


def sign_up(request):
    form = UserCreateForm(request.POST or None)

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

        return redirect('posts')

    return render(request, 'frontend/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required()
def posts(request: WSGIRequest):
    context = {"posts": [], "page": "posts"}
    response = requests.get(
        url=f"{API_URL}posts/",
        cookies=request.COOKIES
    )
    if response.status_code == 200:
        context['posts'] = response.json()

    return render(request, 'frontend/posts/posts.html', context)


@login_required()
def post_detail(request, pk, method):
    post_detail_url = f"{API_URL}posts/{pk}/"
    context = {
        'posts': [],
        'is_detail': True,
        'method': method,
        'page': 'posts'
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
            context['posts'].append(response.json())
        elif response.status_code == 404:
            raise Http404()

    return render(request, 'frontend/posts/posts.html', context)


@login_required()
def post_create(request):
    context = {"form": None, "page": "posts"}
    response = requests.get(
        url=f"{API_URL}chats/",
        cookies=request.COOKIES
    )
    if response.status_code == 200:
        chats_data = format_chats(response.json())
        form = CreatePostForm(data=request.POST, files=request.FILES, chats=chats_data)

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
            form = CreatePostForm(chats=chats_data)

        context['form'] = form

    return render(request, 'frontend/posts/create_post.html', context)


@login_required()
def accounts(request):
    context = {"accounts": [], "page": "accounts"}
    response = requests.get(
        url=f"{API_URL}accounts/",
        cookies=request.COOKIES
    )

    if response.status_code == 200:
        context['accounts'] = response.json()

    return render(request, 'frontend/accounts/accounts.html', context)


@login_required()
def account_create(request, account_type: str):
    if account_type == "instagram":
        form = CreateInstagramAccountForm(request.POST or None)
    elif account_type == "telegram":
        form = CreateTelegramAccountForm(request.POST or None)
    else:
        form = None

    context = {"form": form}
    csrf_token = request.COOKIES.get('csrftoken')

    if request.POST and form.is_valid():
        data = form.cleaned_data
        data['type'] = account_type.capitalize()
        response = requests.post(
            url=f"{API_URL}accounts/",
            data=data,
            cookies=request.COOKIES,
            headers={"X-CSRFToken": csrf_token}
        )
        if response.status_code == 201:
            return redirect('accounts')
        else:
            print("create account", response.text)
    else:
        pass
    return render(request, 'frontend/accounts/create_account.html', context)


@login_required()
def account_delete(request, pk):
    csrf_token = request.COOKIES.get("csrftoken")
    requests.delete(
        url=f"{API_URL}accounts/{pk}",
        cookies=request.COOKIES,
        headers={"X-CSRFToken": csrf_token}
    )

    return redirect("accounts")


@login_required()
def chats(request):
    context = {"page": "chats", "chats": [], "accounts": []}

    response = requests.get(
        url=f"{API_URL}chats/",
        cookies=request.COOKIES
    )
    accounts_response = requests.get(
        url=f"{API_URL}accounts/",
        cookies=request.COOKIES
    )
    if response.status_code == 200 and accounts_response.status_code == 200:
        context['chats'] = response.json()
        context['accounts'] = accounts_response.json()

    return render(request, 'frontend/chats/chats.html', context)


@login_required()
def chat_update(request, account_pk):
    csrf_token = request.COOKIES.get("csrftoken")
    requests.put(
        url=f"{API_URL}chats/",
        data={"account": account_pk},
        cookies=request.COOKIES,
        headers={"X-CSRFToken": csrf_token}
    )

    return redirect('chats')


def home(request):
    return render(request, 'frontend/home.html')
