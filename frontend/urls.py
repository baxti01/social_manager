from django.urls import path, re_path

from frontend.views import login_view, logout_view, home, sign_up, posts, post_detail, post_create

urlpatterns = [
    path('sign-up/', sign_up, name='sign_up'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('posts/', posts, name='posts'),
    path('post/create/', post_create, name='post_create'),
    re_path(r'^posts/(?P<pk>\d+)/(?P<method>(update|delete|$))', post_detail, name='post_detail'),
    #
    # path('accounts/', accounts, name='accounts'),
    # path('accounts/<int:pk>/', account_detail, name='account_detail'),
    #
    # path('chats/', chats, name='chats'),
    # path('chats/<int:pk>/', chat_detail, name='chat_detail'),

    path('', home, name='home'),
]
