import uuid

from django.db import models
from django.contrib.auth.models import User

from .utils import get_choices_list


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram = models.CharField(max_length=25, blank=True, null=True)

    registration = models.DateTimeField(auto_created=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Управляющие"

    def __str__(self):
        return f"{self.id} {self.user.username}"


class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True)
    telegram = models.CharField(max_length=25, blank=True, null=True)

    registration = models.DateTimeField(auto_created=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.id} {self.user.username}"


class Client(models.Model):
    PROJECTS = get_choices_list('projects')
    STATUSES = get_choices_list('clients-statuses', default='conversion')

    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='images/clients/%Y/%m', blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUSES['array'], default=STATUSES['default'])
    project = models.CharField(max_length=100, choices=PROJECTS['array'])

    worker_conversion = models.ForeignKey(Worker, on_delete=models.PROTECT, related_name='conversion')
    worker_retention = models.ForeignKey(Worker, on_delete=models.PROTECT, null=True, blank=True, related_name='retention')

    contact_telegram = models.CharField(max_length=50, blank=True, null=True)
    contact_whatsapp = models.CharField(max_length=50, blank=True, null=True)
    contact_discord = models.CharField(max_length=50, blank=True, null=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.BigIntegerField(blank=True, null=True)

    # location_ip = models.IPAddressField()
    location_city = models.CharField(max_length=100)
    location_country = models.CharField(max_length=100)

    registration = models.DateTimeField(auto_created=True)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name_plural = "Клиенты"
        ordering = ['-registration']

    def __str__(self):
        return self.name


class Comment(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4(), unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    worker = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_created=True)
    text = models.TextField()

    class Meta:
        verbose_name_plural = "Комментарии"
        ordering = ['-date']

    def __str__(self):
        return self.uid


class Deposit(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4(), unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_created=True)
    sum = models.FloatField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Депозиты"
        ordering = ['-date']

    def __str__(self):
        return self.uid


class Withdraw(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4(), unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_created=True)
    sum = models.FloatField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Выводы"
        ordering = ['-date']

    def __str__(self):
        return self.uid
