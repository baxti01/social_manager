from rest_framework import serializers

from social_manager_api.models import Account, Post, Chat, Message


class ChatSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()

    def get_account_type(self, obj):
        return obj.account.type

    def get_fields(self):
        fields = super().get_fields()
        user = self.context.get('request').user

        accounts = Account.objects.filter(user_id=user.pk)
        fields['account'] = serializers.PrimaryKeyRelatedField(
            queryset=accounts
        )

        return fields

    class Meta:
        model = Chat
        fields = [
            'id',
            'chat_id',
            'name',
            'username',
            'user',
            'account',
            'account_type',
        ]
        read_only_fields = [
            'name',
            'chat_id',
            'username',
            'account_type',
            'user'
        ]


class MessageSerializer(serializers.ModelSerializer):
    account_type = serializers.SerializerMethodField()

    def get_account_type(self, obj):
        return obj.account.type

    class Meta:
        model = Message
        fields = ['id', 'message_id', 'account_type', 'chat', 'user']


class AccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(default=None)
    password = serializers.CharField(default=None)
    token = serializers.CharField(
        default=None,
        style={'base_template': 'textarea.html'}
    )
    verification_code = serializers.CharField(default=None)

    def get_fields(self):
        fields = super().get_fields()
        user = self.context['request'].user

        if self.context.get('chats', True):
            chats = Chat.objects.filter(user=user)
            fields['chats'] = ChatSerializer(
                chats, many=True,
                context=self.context,
                read_only=True
            )

        return fields

    class Meta:
        model = Account
        fields = ['id', 'name', 'username', 'password',
                  'verification_code', 'token', 'type', 'user']
        read_only_fields = ['user', 'name']
        extra_kwargs = {'token': {'write_only': True}}


class PostSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        request = self.context['request']
        user = request.user

        chats = Chat.objects.filter(user_id=user.pk)
        accounts = Account.objects.filter(user_id=user.pk)
        message_ids = Message.objects.filter(user_id=user.pk)

        if request.method == 'GET':
            self.context.update({'chats': False})
            fields['accounts'] = AccountSerializer(
                instance=accounts,
                many=True,
                context=self.context
            )
            fields['chats'] = ChatSerializer(
                instance=chats,
                many=True,
                context=self.context
            )
            fields['message_ids'] = MessageSerializer(
                instance=message_ids,
                many=True, context=self.context
            )

            return fields

        fields['chats'] = serializers.PrimaryKeyRelatedField(
            queryset=chats,
            many=True,
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
            'message_ids',
        ]
        read_only_fields = ['user', 'message_ids', 'accounts']
