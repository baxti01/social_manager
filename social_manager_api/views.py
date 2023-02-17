from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.viewsets import GenericViewSet

from social_manager_api.models import Account, Post
from social_manager_api.serializers import AccountSerializer, PostSerializer
from social_manager_api.services import PostService


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        instance, context = self._edit_post(serializer)

        context = self.get_serializer_context()
        if context:
            context['request'].method = 'GET'

        return Response(PostSerializer(instance=instance, context=context).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        headers = self.get_success_headers(serializer.data)

        instance, context = self._edit_post(serializer)

        return Response(
            PostSerializer(instance=instance, context=context),
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def _edit_post(self, serializer):

        PostService().edit_post(
            serializer.validated_data,
            serializer.instance.message_ids.all()
        )

        instance = serializer.save()

        context = self.get_serializer_context()
        if context:
            context['request'].method = 'GET'

        return instance, context

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def perform_destroy(self, instance: Post):
        PostService().delete_post(instance.message_ids.all())
        instance.delete()

    # @action(methods=['put'], detail=True)
    # def post_update(self, ):
    @action(methods=['post'], detail=False)
    def create_text(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = PostService().create_post(
            validated_data=serializer.validated_data,
            user_id=request.user.pk,
            output_serializer=PostSerializer,
            context=self.get_serializer_context()
        )

        return Response(data=data)

    @action(methods=['post'], detail=False)
    def create_photo(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # print(serializer.validated_data)

        data = PostService().create_post(
            validated_data=serializer.validated_data,
            user_id=request.user.pk,
            output_serializer=PostSerializer,
            context=self.get_serializer_context()
        )

        return Response(data=data)

    @action(methods=['post'], detail=False)
    def create_video(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = PostService().create_post(
            validated_data=serializer.validated_data,
            user_id=request.user.pk,
            output_serializer=PostSerializer,
            context=self.get_serializer_context()
        )

        return Response(data=data)

    # dev endpoint
    @action(methods=['delete'], detail=False)
    def delete_all(self, request):
        Post.objects.filter(user_id=request.user.pk).delete()
        return Response(data={"operation": "Delete all records success!"})
