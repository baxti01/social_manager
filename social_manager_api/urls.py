from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social_manager_api.views import AccountViewSet, PostViewSet

router = DefaultRouter()

router.register("accounts", AccountViewSet)
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path('auth/', include('api_auth.urls')),
]
