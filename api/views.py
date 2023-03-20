from django.apps import apps
from django.forms import model_to_dict

from rest_framework import generics, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from .serializers import *
from .permissions import *
from .utils import UserData

# def test(request):
#     print(request.)

# - Manager

class ManagerViewSet(viewsets.ModelViewSet):
    queryset = Manager.objects.all()
    serializer_class = ManagerSerializer

    def get_permissions(self):
        match self.action:
            case 'delete':
                permission_classes = [IsAdminUser]
            case _:
                permission_classes = [IsCurrentUser | IsAdminUser]

        return super(ManagerViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):
        print('override create')

    def update(self, request, *args, **kwargs):
        result = {'status': True, 'description': None, 'data': {}}

        pk = kwargs.get('pk')

        if pk:
            instance_manager = Manager.objects.get(pk=pk)
            instance_manager_user = instance_manager.user

            fields_manager = UserData().field_recognition(request, instance_manager)
            fields_manager_user = UserData().field_recognition(request, instance_manager_user)

            serializer_manager = ManagerSerializer(instance=instance_manager, data=fields_manager)
            serializer_manager_user = UserSerializer(instance=instance_manager, data=fields_manager_user)

            result_manager = UserData().fields_validation(fields_manager, serializer_manager)
            result_manager_user = UserData().fields_validation(fields_manager_user, serializer_manager_user)

            print(serializer_manager_user)

            if result_manager['status']:
                serializer_manager.is_valid()
                serializer_manager.save()

                # result['description'] = result_manager['description']
                result['data'] = serializer_manager.data

            print(result_manager_user)
            if result_manager_user['status']:
                serializer_manager_user.is_valid()
                serializer_manager_user.save()
                # result['description'] = result_manager['description'] % 'manager'
                # result['data'] = result_manager['data']
            return Response(result)
    #
    #     # return super(ManagerViewSet, self).update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        response = {'status': False}
        pk = kwargs.get('pk')

        if pk:
            try:
                pass
                # return super(ManagerViewSet, self).destroy(request, *args, **kwargs)
            except Manager.DoesNotExist:
                pass
        from .renderers import ApiRenderer
        return Response({'dasdasd': 'dsad'})


    @action(methods=['get'], url_name='workers', detail=False)
    def get_workers(self, *args, **kwargs):
        result = {'status': True}
        return Response(result)


#  - Worker
class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        print('override create')
        pass

    def get_permissions(self):
        # list: IsCurrentUser, IsRightManager, IsAdminUser
        # detail: IsCurrentUser, IsRightManager, IsAdminUser
        # update: IsCurrentUser, IsAdminUser
        print(self.action)
        # return super(WorkerViewSet, self).get_permissions()

    def get_queryset(self):
        # compare model with default model User
        print('do')
        print(self.queryset)

    @action(methods=['get'], url_name='clients', detail=False)
    def get_clients(self, *args, **kwargs):
        result = {'status': True}
        return Response(result)

    @action(methods=['get'], url_name='deposits', detail=False)
    def get_deposits(self, *args, **kwargs):
        result = {'status': True}
        return Response(result)

    @action(methods=['get'], url_name='withdraws', detail=False)
    def get_withdraws(self, *args, **kwargs):
        result = {'status': True}
        return Response(result)


# - Clients
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsRightWorker | IsRightManager | IsAdminUser]

    def get_permissions(self):
        # destroy: admin
        print(self.action)
        # return super(ClientViewSet, self).get_permissions()

    @action(methods=['get'], url_name='deposits', detail=False)
    def get_deposits(self, *args, **kwargs):
        result = {'status': True}
        return Response(result)

    @action(methods=['get'], url_name='withdraws', detail=False)
    def get_withdraws(self, *args, **kwargs):
        result = {'status': True}
        return Response()


# - Comments
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsRightWorker | IsRightManager | IsAdminUser]

    def get_permissions(self):
        # delete: admin
        print(self.action)
        # return super(CommentViewSet, self).get_permissions()


# - Deposit
class DepositViewSet(viewsets.ModelViewSet):
    queryset = Deposit.objects.all()
    serializer_class = DepositSerializer
    permission_classes = [IsRightWorker | IsRightManager | IsAdminUser]

    def get_permissions(self):
        # update: admin
        # destroy: admin
        print(self.action)
        return super(DepositViewSet, self).get_permissions()


# - Withdraw
class WithdrawViewSet(viewsets.ModelViewSet):
    queryset = Withdraw.objects.all()
    serializer_class = WithdrawSerializer
    permission_classes = [IsRightWorker | IsRightManager | IsAdminUser]

    def get_permissions(self):
        # update: admin
        # destroy: admin
        print(self.action)
        return super(WithdrawViewSet, self).get_permissions()


# --- TEMPORARY --- #


class CreateRandomObject(views.APIView, UserData):
    def post(self, request, *args, **kwargs):
        result = {'status': False, 'description': None, 'data': {}}
        tables = [model.__name__.lower() for model in apps.get_app_config('api').get_models()]
        mode = kwargs.get('mode')

        if mode:
            if mode in tables:
                serializer, userdata, data = None, dict(), dict()

                match mode:
                    case 'manager':
                        serializer = ManagerSerializer

                        array = self.random_data('user', usertype=mode, data=request.data)
                        userdata, data = array['common'], array['additional']

                    case 'worker':
                        serializer = WorkerSerializer

                        array = self.random_data('user', usertype=mode, data=request.data)
                        userdata, data = array['common'], array['additional']

                    case 'client':
                        serializer = ClientSerializer

                        data = self.random_data('user', usertype=mode, data=request.data)

                    case 'comment':
                        serializer = CommentSerializer

                        data = self.random_data(mode)

                    case 'deposit':
                        serializer = DepositSerializer

                        data = self.random_data(mode)

                    case 'withdraw':
                        serializer = WithdrawSerializer

                        data = self.random_data(mode)

                if userdata:
                    user = User(
                        username=userdata['username'],
                        email=userdata['email'],
                        first_name=userdata['first_name'],
                        last_name=userdata['last_name']
                    )
                    user.set_password(userdata['password'])
                    user.save()

                    data['user'] = user.id

                serialized = serializer(data=data)

                if serialized.is_valid(raise_exception=True):
                    serialized.save()

                    result['status'] = True
                    result['description'] = f"{mode.capitalize()} has been added"
                    result['data'] = self.format_object(serialized.data)

                if 'photo' in data:
                    self.remove_temporary_file(data['photo'])

            else:
                result['description'] = "Mode not recognized"
        else:
            result['description'] = "Value «Mode» not set"

        return Response(result)
