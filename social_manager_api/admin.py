from django.contrib import admin
from social_manager_api.models import Account, Post


# Register your models here.
class AccountModel(admin.ModelAdmin):
    list_display = ('id', "type", "token", "user")
    list_display_links = ('id', 'type')
    search_fields = ('id', 'type', "token")
    list_filter = ('type', 'user')


class PostModel(admin.ModelAdmin):
    list_display = ('id', "title", "account", "user")
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title')
    list_filter = ('title', "account", 'user')


admin.site.register(Account, AccountModel)
admin.site.register(Post, PostModel)
