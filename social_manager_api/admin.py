from django.contrib import admin

from social_manager_api.models import Account, Post, Chat, Message


# Register your models here.
class AccountModel(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'token', 'user')
    list_display_links = ('id', 'name', 'type')
    search_fields = ('id', 'type', 'token')
    list_filter = ('type', 'user')
    ordering = ['id']


class PostModel(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_accounts', 'user')
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title')
    list_filter = ('title', 'accounts', 'user')
    ordering = ['id']

    def get_accounts(self, obj):
        return '\n'.join([a.type for a in obj.accounts.all()])


class ChatModel(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'name', 'username', 'account_type', 'user')
    list_display_links = ('id', 'chat_id', 'name', 'account_type')
    search_fields = ('id', 'chat_id', 'account_type', 'user')
    list_filter = ('id', 'chat_id', 'name', 'user')
    ordering = ['id']

    def account_type(self, obj):
        return obj.account.type


class MessageModel(admin.ModelAdmin):
    list_display = ('id', 'message_id', 'account_type', 'chat',)
    list_display_links = ('id', 'message_id', 'account_type')
    search_fields = ('id', 'message_id', 'account_type', 'chat',)
    list_filter = ('id', 'message_id', 'chat',)
    ordering = ['id']

    def account_type(self, obj):
        return obj.account.type


admin.site.register(Account, AccountModel)
admin.site.register(Post, PostModel)
admin.site.register(Chat, ChatModel)
admin.site.register(Message, MessageModel)
