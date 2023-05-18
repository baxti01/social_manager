from django.urls import path, re_path

from frontend.views import login_view, logout_view, home, sign_up, posts, post_detail, post_create, accounts, \
    account_create, account_delete, chats, chat_update

urlpatterns = [
    path('sign-up/', sign_up, name='sign_up'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('posts/', posts, name='posts'),
    path('post/create/', post_create, name='post_create'),
    re_path(r'^posts/(?P<pk>\d+)/(?P<method>(update|delete|$))', post_detail, name='post_detail'),

    path('accounts/', accounts, name='accounts'),
    path('accounts/<int:pk>/', account_delete, name='account_delete'),
    re_path(r'^accounts/create/(?P<account_type>(instagram|telegram))/$', account_create, name='account_create'),

    path('chats/', chats, name='chats'),
    path('chats/account/<int:account_pk>/', chat_update, name='chat_update'),

    path('', home, name='home'),
]
