from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Follow, User


class FollowInline(admin.StackedInline):
    model = Follow
    fk_name = 'user'
    extra = 2


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('id', 'username')
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username',)
    empty_value_display = '-пусто-'
    inlines = (FollowInline,)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'following',
    )
    search_fields = (
        'user',
        'following',
    )
    raw_id_fields = ('user', 'following')
    autocomplete_fields = ('user', 'following')


admin.site.site_header = 'Администрирование Foodgram'
admin.site.site_title = 'Admin-Foodgram'
admin.site.index_title = 'Главная страница Администратора'
admin.site.empty_value_display = 'Не задано'
