from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from social_manager_api.exceptions import MessageTypeError
from social_manager_api.models import Account, Post
from social_manager_api.serializers import AccountSerializer, PostSerializer
from social_manager_api.services import PostService


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.pk)

    def get_queryset(self):
        return Account.objects.filter(user_id=self.request.user.pk)


class PostViewSet(mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(
            user_id=self.request.user.pk,
        )

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

        photo = serializer.validated_data.get('photo', None)
        video = serializer.validated_data.get('video', None)

        if (not instance.photo or not instance.video) and (photo or video):
            raise MessageTypeError()

        PostService().edit_post(
            serializer.validated_data,
            serializer.instance.message_ids.all()
        )

        context = self._change_context()

        return Response(PostSerializer(instance=instance, context=context).data)

    def _change_context(self):
        context = self.get_serializer_context()
        if context:
            context['request'].method = 'GET'

        return context

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def perform_destroy(self, instance: Post):
        PostService().delete_post(instance.message_ids.all())
        instance.delete()

    # dev endpoint
    @action(methods=['delete'], detail=False)
    def delete_all(self, request):
        Post.objects.filter(user_id=request.user.pk).delete()
        return Response(data={"operation": "Delete all records success!"})
