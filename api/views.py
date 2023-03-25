import requests

from django.apps import apps
from django.contrib.auth.models import Group
from django.db.models import Q
from rest_framework import generics, views, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import *
from .permissions import *
from .utils import RandomDataMixin, ViewSetMixin


class ManagerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(Q(role='manager') & Q(groups__name='Managers'))
    serializer_class = ManagerSerializer
    permission_classes = [IsAdmin | IsCurrentUser]

    def get_permissions(self):
        match self.action:
            case 'list' | 'create' | 'destroy':
                return [IsAdmin()]
            case _:
                return super().get_permissions()

    @action(
        methods=['get'],
        detail=True,
        url_name='manager-workers',
        permission_classes=[IsAdmin | ActionCurrentManager]
    )
    def workers(self, *args, **kwargs):

        workers = User.objects.filter(Q(role='worker') & Q(manager=kwargs.get('pk')))

        workers_conversion = WorkerSerializer(workers.filter(groups__name='Conversion'), many=True)
        workers_retention = WorkerSerializer(workers.filter(groups__name='Retention'), many=True)

        result = {
            'status': True,
            'description': 'Manager\'s workers has been received',
            'data': {
                'conversion': workers_conversion.data,
                'retention': workers_retention.data
            }
        }
        return Response(result)


# WORKERS

class WorkerViewSet(viewsets.ModelViewSet, ViewSetMixin):
    queryset = User.objects.filter(
        Q(role='worker') & (Q(groups__name='Conversion') | Q(groups__name='Retention'))
    ).order_by('-pk')

    def get_queryset(self):
        if self.request.user.role == 'manager':
            self.queryset = self.queryset.filter(manager=self.request.user)

        return super(WorkerViewSet, self).get_queryset()

    def get_serializer_class(self):
        return self.recognize_serializer('worker', self.action, self.request.user.role)

    def get_permissions(self):
        self.permission_classes = self.recognize_permissions('worker', self.action)

        return super(WorkerViewSet, self).get_permissions()

    @action(
        methods=['get'],
        detail=True,
        url_name='worker-manager',
        permission_classes=[IsAdmin],  # IsAdmin, ActionCurrentWorker
    )
    def manager(self):
        result = {
            'status': True,
            'description': 'Worker\'s manager has been received',
            'data': "IN PROCESS"
        }
        return Response(result)

    @action(
        methods=['get'],
        detail=True,
        url_name='worker-clients',
        permission_classes=[IsAdmin],  # IsAdmin, ActionCurrentWorker, ActionCurrentWorker
    )
    def clients(self):
        result = {
            'status': True,
            'description': 'Worker\'s clients has been received',
            'data': "IN PROCESS"
        }
        return Response(result)

    @action(
        methods=['partial_update'],
        detail=True,
        url_name='worker-update-password',
        permission_classes=[IsAdmin],  # IsAdmin, ActionCurrentWorker, ActionCurrentWorker
    )
    def update_password(self):
        result = {
            'status': True,
            'description': 'Worker\'s password has been updated successfully',
            'data': "IN PROCESS"
        }
        return Response(result)


# --- TEMPORARY --- #


class CreateRandomObject(views.APIView, RandomDataMixin):
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        result = {'status': False, 'description': None, 'data': {}}
        mode, serializer = kwargs.get('mode'), None

        match mode:
            case 'manager':
                serializer = ManagerSerializer

            case 'worker':
                serializer = WorkerCreationSerializer

            case 'client':
                serializer = ClientSerializer

            case 'comment':
                serializer = CommentSerializer

            case 'deposit':
                serializer = DepositSerializer

            case 'withdraw':
                serializer = WithdrawSerializer

            case _:
                result['description'] = "Mode not recognize"

        if serializer is not None:
            data = self.random_data(mode, data=request.data)
            print(data['data'])

            if not data['status']:
                return Response(data)

            serializer = serializer(data=data['data'])
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if 'type' in data:
                group = Group.objects.get(name=data['type'])

                user = User.objects.get(username=serializer.data['username'])
                user.groups.add(group)

            result['status'] = True
            result['description'] = f"{mode.capitalize()} has been added successfully"
            result['data'] = serializer.data

        return Response(result)
