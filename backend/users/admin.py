from django.contrib import admin
from django.contrib.auth import get_user_model

from users.models import Follow

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'first_name', 'last_name')
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('username',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')
    search_fields = ('author', 'user')
