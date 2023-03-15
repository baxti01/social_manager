from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api_auth.views import UserView, UserCreateView, login_facebook, complete_facebook, home

urlpatterns = [
    path('users/me/', UserView.as_view()),
    path('users/create/', UserCreateView.as_view()),
    path('session/', include('rest_framework.urls')),
    path('jwt/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path("login/<str:backend>/", login_facebook, name='login'),
    path("complete/<str:backend>/", complete_facebook, name="complete"),
    path("home/", home, name="home"),
]
