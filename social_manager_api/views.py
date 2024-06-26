from rest_framework import viewsets, status, mixins, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from social_manager_api.models import Account, Post, Message, Chat
from social_manager_api.serializers import AccountSerializer, PostSerializer, ChatSerializer
from social_manager_api.services import PostService, AccountService, ChatService


class AccountViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = AccountService().create_account(
            validated_data=serializer.validated_data,
            user_id=request.user.pk
        )

        serializer.instance = instance

        headers = self.get_success_headers(serializer.data)

        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def get_queryset(self):
        return Account.objects.filter(
            user_id=self.request.user.pk
        ).order_by('-updated_at')


class ChatViewSet(mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, *args, **kwargs)
        serializer.is_valid(raise_exception=True)
        account = serializer.validated_data['account']

        ChatService().update_chats(
            session_id=account.token,
            account_id=account.pk,
            user_id=account.user_id,
            account_type=account.type
        )
        return Response({"message": "chats successfully updated!"})

    def get_queryset(self):
        return Chat.objects.filter(
            user_id=self.request.user.pk
        ).order_by('-updated_at')


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(
            user_id=self.request.user.pk,
        ).order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = PostService().create_post(
            validated_data=serializer.validated_data,
            user_id=request.user.pk,
        )

        serializer.instance = instance

        headers = self.get_success_headers(serializer.data)

        context = self._change_context()

        return Response(
            PostSerializer(instance=instance, context=context).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance: Post = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        PostService().edit_post(
            serializer.validated_data,
            serializer.instance.message_ids.all()
        )

        context = self._change_context()

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(PostSerializer(instance=instance, context=context).data)

    def perform_destroy(self, instance: Post):
        PostService().delete_post(instance.message_ids.all())

        instance.delete()

    def _change_context(self):
        context = self.get_serializer_context()
        if context:
            context['request'].method = 'GET'

        return context

    # dev endpoint
    @action(methods=['delete'], detail=False)
    def delete_all(self, request):
        Post.objects.filter(user_id=request.user.pk).delete()
        messages = Message.objects.filter(user_id=request.user.pk).all()
        PostService().delete_post(messages)
        return Response(data={"operation": "Delete all records success!"})
