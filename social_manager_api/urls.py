from django.urls import path, include

from social_manager_api.routers import ChatRouter, MyDefaultRouter
from social_manager_api.views import AccountViewSet, PostViewSet, ChatViewSet

router = MyDefaultRouter()
chat_router = ChatRouter()

router.register("accounts", AccountViewSet)
router.register("posts", PostViewSet)

chat_router.register('chats', ChatViewSet)

router.include_router(chat_router)

urlpatterns = [
    path("", include(router.urls)),
    path('auth/', include('api_auth.urls')),
]
