from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *
from .handler import custom_titled_filter


class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)
    list_display_links = ('username',)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_html_avatar', 'project', 'status', 'location_country')
    list_display_links = ('id', 'name', 'project')
    list_filter = (
        ('worker_conversion', custom_titled_filter('Конверсия')),
        ('worker_retention', custom_titled_filter('Ретеншн')),
        ('project', custom_titled_filter('Проект')),
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

    def get_html_avatar(self, data):
        if data.photo:
            return mark_safe(f"<img src='{data.photo.url}' width=50>")


class CommentAdmin(admin.ModelAdmin):
    list_display = ('uid', 'client')
    list_display_links = ('uid', 'client')
    list_filter = (
        ('date', custom_titled_filter('Дата создания')),
    )
    search_fields = ('client', 'worker')
    # readonly_fields = ('id', )


class DepositAdmin(admin.ModelAdmin):
    list_display = ('uid', 'date', 'sum')
    list_display_links = ('uid',)
    list_filter = (
        ('client', custom_titled_filter('Клиент')),
        ('date', custom_titled_filter('Дата создания'))
    )
    list_editable = ('sum',)
    search_fields = ('id', 'uid', 'client')
    # readonly_fields = ('id', 'uid')


class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('uid', 'date', 'sum')
    list_display_links = ('uid',)
    list_filter = (
        ('client', custom_titled_filter('Клиент')),
        ('date', custom_titled_filter('Дата создания'))
    )
    list_editable = ('sum',)
    search_fields = ('id', 'uid', 'client')
    # readonly_fields = ('id', 'uid')


admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Withdraw, WithdrawAdmin)
