from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *
from .handler import custom_titled_filter


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role')
    list_display_links = ('username',)

    list_filter = (
        ('role', custom_titled_filter('Тип пользователя')),
        ('date_joined', custom_titled_filter('Регистрация')),
        ('last_login', custom_titled_filter('Последний вход')),
        ('groups', custom_titled_filter('Группы')),
    )
    search_fields = ('id', 'username')
    readonly_fields = ('role', 'date_joined', 'last_login')

    save_on_top = True


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'picture', 'project', 'status', 'location_country')
    list_display_links = ('id', 'name', 'project')
    list_filter = (
        ('project', custom_titled_filter('Проект')),
        ('status', custom_titled_filter('Статус')),
        ('registration', custom_titled_filter('Дата регистрации')),
        ('updated', custom_titled_filter('Дата обновления'))
    )
    list_editable = ('status',)
    search_fields = (
        'name', 'status', 'project',
        'worker_conversion', 'worker_retention',
        'contact_telegram', 'contact_whatsapp', 'contact_discord', 'contact_email', 'contact_phone',
        'location_city', 'location_country'
    )
    readonly_fields = ('id', 'updated')

    save_on_top = True

    def picture(self, data):
        if data.photo:
            return mark_safe(f"<img src='{data.photo.url}' width=50>")


class CommentAdmin(admin.ModelAdmin):
    list_display = ('uid', 'client', 'staff')
    list_display_links = ('uid',)
    list_filter = (
        ('date', custom_titled_filter('Дата создания')),
    )
    search_fields = ('client', 'staff')


class DepositAdmin(admin.ModelAdmin):
    list_display = ('uid', 'date', 'sum', 'client')
    list_display_links = ('uid',)
    list_filter = (
        ('client', custom_titled_filter('Клиент')),
        ('date', custom_titled_filter('Дата создания'))
    )
    list_editable = ('sum',)
    search_fields = ('id', 'uid', 'client')


class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('uid', 'date', 'sum', 'client')
    list_display_links = ('uid',)
    list_filter = (
        ('client', custom_titled_filter('Клиент')),
        ('date', custom_titled_filter('Дата создания'))
    )
    list_editable = ('sum',)
    search_fields = ('id', 'uid', 'client')


admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Withdraw, WithdrawAdmin)
