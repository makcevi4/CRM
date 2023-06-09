from django.core.exceptions import ValidationError
from rest_framework import views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import *
from .permissions import *
from .utils import RandomDataMixin, ViewSetMixin


class ManagerViewSet(viewsets.ModelViewSet, ViewSetMixin):
    queryset = User.objects.filter(Q(role='manager') & Q(groups__name='Managers'))
    serializer_class = ManagerSerializer

    def get_permissions(self):
        self.permission_classes = self.recognize_permissions('manager', self.action)

        return super(ManagerViewSet, self).get_permissions()

    @action(
        methods=['get'],
        detail=True,
        url_name='manager-workers'
    )
    def workers(self, *args, **kwargs):
        workers = User.objects.filter(Q(role='worker') & Q(manager=kwargs.get('pk')))

        workers_conversion = ManagerWorkersSerializer(
            workers.filter(groups__name='Conversion').order_by('-pk'),
            many=True
        )
        workers_retention = ManagerWorkersSerializer(
            workers.filter(groups__name='Retention').order_by('-pk'),
            many=True
        )

        result = {
            'status': True,
            'description': 'Manager\'s workers has been received',
            'data': {
                'conversion': workers_conversion.data,
                'retention': workers_retention.data
            }
        }
        return Response(result)

    # Endpoint: Manager comments
    @action(
        methods=['get'],
        detail=True,
        url_name='manager-comments'

    )
    def comments(self, *args, **kwargs):
        result = {
            'status': True,
            'description': "Manager comments has been received",
            'data': {}
        }

        try:
            user = User.objects.get(pk=kwargs.get('pk'))

            if user.role == 'manager' and self.recognize_user_type(user) == 'managers':
                comments = Comment.objects.filter(staff=user.pk)
                serializer = CommentStaffSerializer(comments, many=True)

                result['data'] = self.get_paginated_response(serializer.data)
            else:
                result['status'] = False
                result['description'] = "The specified user isn't a manager"

        except ValueError:
            result['status'] = False
            result['description'] = "The specified value isn't correct"
        except User.DoesNotExist:
            result['status'] = False
            result['description'] = "The specified manager not found"

        return Response(result)


# WORKERS

class WorkerViewSet(viewsets.ModelViewSet, ViewSetMixin):
    queryset = User.objects.filter(
        Q(role='worker') & (Q(groups__name='Conversion') | Q(groups__name='Retention'))
    ).order_by('-pk')

    def get_queryset(self):
        if not self.request.user.is_anonymous and self.request.user.role == 'manager':
            self.queryset = self.queryset.filter(manager=self.request.user)

        return super(WorkerViewSet, self).get_queryset()

    def get_serializer_class(self):
        return self.recognize_serializer('worker', self.action, self.request.user.role)

    def get_permissions(self):
        self.permission_classes = self.recognize_permissions('worker', self.action)

        return super(WorkerViewSet, self).get_permissions()

    #  Endpoint: Worker manager
    @action(
        methods=['get'],
        detail=True,
        url_name='worker-manager'
    )
    def manager(self, *args, **kwargs):
        result = {
            'status': True,
            'description': "Worker's manager has been received",
            'data': {}
        }

        pk = kwargs.get('pk')

        try:
            worker = self.queryset.get(pk=pk)
            manager = User.objects.get(Q(role='manager') & Q(groups__name='Managers') & Q(pk=worker.manager.pk))

            serializer = ManagerSerializer(manager)
            result['data'] = serializer.data

        except User.DoesNotExist:
            result['status'] = False
            result['description'] = "Manager of current worker doesn't found"

        return Response(result)

    # Endpoint: Worker clients
    @action(
        methods=['get'],
        detail=True,
        url_name='worker-clients'
    )
    def clients(self, *args, **kwargs):
        client_filter = None

        result = {
            'status': True,
            'description': "Worker's clients has been received",
            'data': {}
        }

        worker = User.objects.get(role='worker', pk=kwargs.get('pk'))
        match self.recognize_user_type(worker):
            case 'conversion':
                client_filter = Q(worker_conversion=worker.pk)
            case 'retention':
                client_filter = Q(worker_retention=worker.pk)

        clients = Client.objects.filter(client_filter)
        serializer = ClientSerializer(clients, many=True)

        result['data'] = serializer.data

        if not len(serializer.data):
            result['description'] = "No clients"

        return Response(result)

    # Endpoint: Worker comments
    @action(
        methods=['get'],
        detail=True,
        url_name='worker-comments'

    )
    def comments(self, *args, **kwargs):
        result = {
            'status': True,
            'description': "Worker comments has been received",
            'data': {}
        }

        try:
            user = User.objects.get(pk=kwargs.get('pk'))
            usertype = self.recognize_user_type(user)

            if user.role == 'worker' and (usertype == 'conversion' or usertype == 'retention'):
                comments = Comment.objects.filter(staff=user.pk)
                serializer = CommentStaffSerializer(comments, many=True)

                result['data'] = serializer.data

            else:
                result['status'] = False
                result['description'] = "The specified user isn't a worker"

        except ValueError:
            result['status'] = False
            result['description'] = "The specified value isn't correct"

        except User.DoesNotExist:
            result['status'] = False
            result['description'] = "The specified worker not found"

        return Response(result)

    # Endpoint: Worker update password
    @action(
        methods=['patch'],
        detail=True,
        url_name='worker-update-password',
        url_path='update/password'
    )
    def update_password(self, *args, **kwargs):
        pk = kwargs.get('pk')
        result = {
            'status': True,
            'description': "Worker's password has been updated successfully",
            'data': {}
        }

        instance = User.objects.get(pk=pk)
        serializer = WorkerPasswordUpdateSerializer(instance, self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        instance.set_password(self.request.data['password'])
        instance.save()

        return Response(result)


# Clients

class ClientViewSet(viewsets.ModelViewSet, ViewSetMixin):
    queryset = Client.objects.all()

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            match self.request.user.role:
                case 'manager':
                    workers_conversion = self.queryset.filter(
                        Q(role='worker') &
                        Q(groups__name='Conversion') &
                        Q(manager=self.request.user.pk)
                    )

                    workers_retention = self.queryset.filter(
                        Q(role='worker') &
                        Q(groups__name='Retention') &
                        Q(manager=self.request.user.pk)
                    )

                    workers_conversion_clients = Client.objects.filter(worker_conversion__in=workers_conversion)
                    workers_retention_clients = Client.objects.filter(worker_retention__in=workers_retention)

                    self.queryset = workers_conversion_clients | workers_retention_clients

                case 'worker':
                    worker_filter, worker_type = None, self.recognize_user_type(self.request.user)

                    match worker_type:
                        case 'conversion':
                            worker_filter = Q(worker_conversion=self.request.user.pk)
                        case 'retention':
                            worker_filter = Q(worker_retention=self.request.user.pk)

                    clients = Client.objects.filter(worker_filter)
                    self.queryset = clients

        return super(ClientViewSet, self).get_queryset()

    def get_serializer_class(self):
        return self.recognize_serializer('client', self.action, self.request.user.role)

    def get_permissions(self):
        self.permission_classes = self.recognize_permissions('client', self.action)
        
        return super(ClientViewSet, self).get_permissions()

    # Endpoint: Client comments
    @action(
        methods=['get'],
        detail=True,
        url_name='client-comments'

    )
    def comments(self, *args, **kwargs):
        pk, user_role = kwargs.get('pk'), self.request.user.role

        comments = Comment.objects.filter(client=pk)

        serializer = CommentSerializer if user_role == 'admin' or not user_role else CommentStaffSerializer
        serializer = serializer(comments, many=True)

        return Response({
            'status': True,
            'description': "Client comments has been received",
            'data': serializer.data
        })

    # Endpoint: Client deposits
    @action(
        methods=['get'],
        detail=True,
        url_name='client-deposits',
    )
    def deposits(self, *args, **kwargs):
        deposits = Deposit.objects.filter(client=kwargs.get('pk'))
        serializer = DepositSerializer(deposits, many=True)

        result = {
            'status': True,
            'description': "Client deposits has been received",
            'data': serializer.data
        }

        return Response(result)

    # Endpoint: Client withdraws
    @action(
        methods=['get'],
        detail=True,
        url_name='client-withdraws'

    )
    def withdraws(self, *args, **kwargs):
        withdraws = Deposit.objects.filter(client=kwargs.get('pk'))
        serializer = DepositSerializer(withdraws, many=True)

        result = {
            'status': True,
            'description': "Client withdraws has been received",
            'data': serializer.data
        }

        return Response(result)

    # Endpoint: Client workers
    @action(
        methods=['get'],
        detail=True,
        url_name='client-workers',
    )
    def workers(self, *args, **kwargs):
        client = Client.objects.get(pk=kwargs.get('pk'))

        serializer_conversion = WorkerSerializer(client.worker_conversion)
        serializer_retention = WorkerSerializer(client.worker_retention)

        result = {
            'status': True,
            'description': "Client workers has been received",
            'data': {
                'conversion': serializer_conversion.data if client.worker_conversion else None,
                'retention': serializer_retention.data if client.worker_retention else None
            }
        }

        return Response(result)


# Comments


class CommentViewSet(viewsets.ModelViewSet, ViewSetMixin):
    queryset = Comment.objects.all()

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            match self.request.user.role:
                case 'manager' | 'worker':
                    self.queryset = self.queryset.filter(staff=self.request.user.pk)

        return super(CommentViewSet, self).get_queryset()

    def get_serializer_class(self):
        return self.recognize_serializer('comment', self.action, self.request.user)

    def get_permissions(self):
        self.permission_classes = self.recognize_permissions('comment', self.action)
        return super(CommentViewSet, self).get_permissions()

    def perform_create(self, serializer):
        serializer.save(staff=self.request.user)

    @action(
        methods=['get'],
        detail=True,
        url_name='comment-client'
    )
    def client(self, *args, **kwargs):
        pk = kwargs.get('pk')
        result = {
            'status': True,
            'description': "Client withdraws has been received",
            'data': {}
        }

        try:
            comment = Comment.objects.get(uid=pk)
            serializer = ClientSerializer(comment.client)

            result['data'] = serializer.data

        except ValidationError as error:
            result['status'] = False
            result['description'] = error.message % error.params

        return Response(result)


# - Deposits


class DepositViewSet(viewsets.ModelViewSet, ViewSetMixin):
    queryset = Deposit.objects.all()

    def get_permissions(self):
        self.permission_classes = self.recognize_permissions('deposit', self.action)
        return super(DepositViewSet, self).get_permissions()

    def get_serializer_class(self):
        return self.recognize_serializer('deposit', self.action, self.request.user)

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            match self.request.user.role:
                case 'manager':
                    workers = User.objects.filter(
                        Q(role='worker') & (Q(groups__name='Conversion') | Q(groups__name='Retention')) &
                        Q(manager=self.request.user)
                    )
                    clients = Client.objects.filter(Q(worker_conversion__in=workers) | Q(worker_retention__in=workers))
                    self.queryset = self.queryset.filter(client__in=clients)

                case 'worker':
                    clients = Client.objects.filter(
                        Q(worker_conversion=self.request.user) | Q(worker_retention=self.request.user)
                    )
                    self.queryset = self.queryset.filter(client__in=clients)

        return super(DepositViewSet, self).get_queryset()


# - Withdraws


class WithdrawViewSet(viewsets.ModelViewSet, ViewSetMixin):
    queryset = Withdraw.objects.all()

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            match self.request.user.role:
                case 'manager':
                    workers = User.objects.filter(
                        Q(role='worker') & (Q(groups__name='Conversion') | Q(groups__name='Retention')) &
                        Q(manager=self.request.user)
                    )
                    clients = Client.objects.filter(Q(worker_conversion__in=workers) | Q(worker_retention__in=workers))
                    self.queryset = self.queryset.filter(client__in=clients)

                case 'worker':
                    clients = Client.objects.filter(
                        Q(worker_conversion=self.request.user) | Q(worker_retention=self.request.user)
                    )
                    self.queryset = self.queryset.filter(client__in=clients)

        return super(WithdrawViewSet, self).get_queryset()

    def get_serializer_class(self):
        return self.recognize_serializer('withdraw', self.action, self.request.user)

    def get_permissions(self):
        self.permission_classes = self.recognize_permissions('withdraw', self.action)
        return super(WithdrawViewSet, self).get_permissions()


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

            if not data['status']:
                return Response(data)

            serializer = serializer(data=data['data'])
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if 'type' in data:
                group = Group.objects.get(name=data['type'])

                user = User.objects.get(username=serializer.data['username'])
                user.groups.add(group)

            if 'photo' in data['data']:
                self.remove_temporary_file(data['data']['photo'])

            result['status'] = True
            result['description'] = f"{mode.capitalize()} has been added successfully"
            result['data'] = serializer.data

        return Response(result)
