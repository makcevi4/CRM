import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

from .handler import get_choices_list


class User(AbstractUser):
    ROLES = get_choices_list('staff-roles')

    telegram = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(max_length=50, choices=ROLES['array'])
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "персонал"
        verbose_name_plural = "Персонал"

    def __str__(self):
        return self.username


class Client(models.Model):
    PROJECTS = get_choices_list('projects')
    STATUSES = get_choices_list('clients-statuses', default='conversion')

    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='images/clients/%Y/%m/', blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUSES['array'], default=STATUSES['default'])
    project = models.CharField(max_length=100, choices=PROJECTS['array'], null=True, blank=True)

    worker_conversion = models.ForeignKey(User, on_delete=models.PROTECT, related_name='conversion')
    worker_retention = models.ForeignKey(User, on_delete=models.PROTECT,  related_name='retention',
                                         null=True, blank=True)

    contact_telegram = models.CharField(max_length=50, blank=True, null=True)
    contact_whatsapp = models.CharField(max_length=50, blank=True, null=True)
    contact_discord = models.CharField(max_length=50, blank=True, null=True)
    contact_phone = models.BigIntegerField(blank=True, null=True)

    location_city = models.CharField(max_length=100)
    location_country = models.CharField(max_length=100)

    registration = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = "клиента"
        verbose_name_plural = "Клиенты"
        ordering = ['-registration']

    def __str__(self):
        return self.name


# class Documents(models.Model):
#     client = models.OneToOneField(Client, unique=True, on_delete=models.CASCADE)
#     serial = models.CharField(max_length=50, null=True, blank=True)
#     date = models.DateField(null=True, blank=True)
#     passport_front = models.ImageField(upload_to='images/documents/%Y/%m/', blank=True, null=True)
#     passport_back = models.ImageField(upload_to='images/documents/%Y/%m/', blank=True, null=True)


class Comment(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    text = models.TextField()

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-date']

    def __str__(self):
        return str(self.uid)


class Deposit(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    sum = models.FloatField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "депозит"
        verbose_name_plural = "Депозиты"
        ordering = ['-date']

    def __str__(self):
        return str(self.uid)


class Withdraw(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    sum = models.FloatField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "вывод"
        verbose_name_plural = "Выводы"
        ordering = ['-date']

    def __str__(self):
        return str(self.uid)
