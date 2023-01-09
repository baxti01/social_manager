from rest_framework import viewsets

from social_manager_api.models import Account, Post
from social_manager_api.serializers import AccountSerializer, PostSerializer


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        return Account.objects.filter(user_id=self.request.user.pk)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(user_id=self.request.user.pk)
