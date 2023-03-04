from rest_framework import serializers

from social_manager_api.models import Account, Post, Chat, Message


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'type', 'token', 'user']
        read_only_fields = ['user']
        extra_kwargs = {'token': {'write_only': True}}


class ChatSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()

    def get_account_type(self, obj):
        return obj.account.type

    class Meta:
        model = Chat
        fields = ['id', 'chat_id', 'account_type', 'user']


class MessageSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()

    def get_account_type(self, obj):
        return obj.account.type

    class Meta:
        model = Message
        fields = ['id', 'message_id', 'account_type', 'chat', 'user']


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
        read_only_fields = ['user', 'message_ids', 'accounts']
