from django.apps import apps
from rest_framework import generics, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .serializers import *
from .permissions import *
from .utils import RandomDataMixin


class ListManagersView(generics.ListAPIView):
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = ManagerSerializer


class DetailManagersView(generics.RetrieveAPIView):
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = ManagerSerializer


class CreateManagerView(generics.CreateAPIView):
    queryset = User.objects.filter(groups__name='Managers')
    serializer_class = ManagerSerializer


class CreateManagerView(generics.CreateAPIView):
    pass
