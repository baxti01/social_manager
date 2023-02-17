from django.http import HttpRequest
from rest_framework import serializers
from rest_framework.request import Request

from social_manager_api.models import Account, Post, Chat, Message


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'type', 'token', 'user']
        # fields = '__all__'


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['id', 'chat_id', 'account_type', 'user']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'message_id', 'account_type', 'chat', 'user']


# class CreateBaseSerializer(serializers.Serializer):
#     # chat_id = serializers.CharField(default='me')
#     title = serializers.CharField(max_length=255)
#     description = serializers.CharField()
#     hash_tag = serializers.CharField()
#     parse_mode = serializers.ChoiceField(
#         choices=Post.ParseModeChoices.choices,
#         allow_null=True,
#         default=Post.ParseModeChoices.DEFAULT
#     )
#
#     def get_fields(self):
#         fields = super().get_fields()
#
#         user = self.context.get('request').user
#         print(self.context.get('request'))
#
#         accounts = Account.objects.filter(user_id=user.pk)
#         fields['accounts'] = serializers.PrimaryKeyRelatedField(
#             queryset=accounts,
#             many=True,
#             required=True,
#             allow_null=False
#         )
#
#         chats = Chat.objects.filter(user_id=user.pk)
#         fields['chats'] = serializers.PrimaryKeyRelatedField(
#             queryset=chats,
#             many=True,
#             required=True,
#             allow_null=False
#         )
#
#         return fields

#
# class CreateTextPostSerializer(CreateBaseSerializer):
#     pass
#
#
# class CreatePhotoPostSerializer(CreateBaseSerializer):
#     photo = serializers.ImageField(max_length=100, allow_null=False, required=True)
#
#
# class CreateVideoPostSerializer(CreateBaseSerializer):
#     video = serializers.FileField(max_length=100, allow_null=False, required=True)


class PostSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        user = request.user

        chats = Chat.objects.filter(user_id=user.pk)
        accounts = Account.objects.filter(user_id=user.pk)
        message_ids = Message.objects.filter(user_id=user.pk)

        if request.method == 'GET':
            fields['accounts'] = AccountSerializer(instance=accounts, many=True)
            fields['chats'] = ChatSerializer(instance=chats, many=True)
            fields['message_ids'] = MessageSerializer(instance=message_ids, many=True)

            return fields

        fields['accounts'] = serializers.PrimaryKeyRelatedField(
            queryset=accounts,
            many=True,
            required=True,
            allow_null=False
        )

        fields['chats'] = serializers.PrimaryKeyRelatedField(
            queryset=chats,
            many=True,
            required=True,
            allow_null=False
        )

        if request.method == 'PUT':
            fields['chats'].read_only = True

        return fields

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'hash_tag',
            'photo',
            'video',
            'parse_mode',
            'user',
            'accounts',
            'chats',
            'message_ids',
        ]
        read_only_fields = ['user', 'message_ids']
        # fields = '__all__'
