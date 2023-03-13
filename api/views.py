from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework import generics, views
from rest_framework.response import Response
from django.apps import apps

from .utils import get_random_data
from .serializers import *
from .permissions import *


# --- TEMPORARY --- #

class CreateRandomObject(views.APIView):
    def post(self, request, *args, **kwargs):
        result = {'status': False, 'description': None, 'data': None}
        tables = [model.__name__.lower() for model in apps.get_app_config('api').get_models()]
        mode = kwargs.get('mode')

        if mode:
            if mode in tables:
                serializer, userdata, data = None, dict(), dict()

                match mode:
                    case 'manager':
                        array = get_random_data('user', usertype=mode, data=request.data)
                        userdata = array['common']
                        data = array['additional']

                        serializer = ManagerSerializer

                    case 'worker':
                        array = get_random_data('user', usertype=mode, data=request.data,
                                                managers=Manager.objects.all())

                        userdata = array['common']
                        data = array['additional']

                        serializer = WorkerSerializer

                    case 'client':
                        workers = {
                            'conversion': Worker.objects.filter(type='conversion'),
                            'retention': Worker.objects.filter(type='retention')
                        }

                        data = get_random_data('user', usertype=mode, data=request.data, workers=workers)

                        serializer = ClientSerializer

                    case 'comment':

                        serializer = CommentSerializer

                    case 'deposit':
                        data = {

                        }
                        serializer = DepositSerializer

                    case 'withdraw':
                        data = {

                        }
                        serializer = WithdrawSerializer

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
                    result['data'] = dict()

                    for key, value in serialized.data.items():
                        match key:
                            case 'user':
                                value = model_to_dict(User.objects.get(pk=value))
                            case 'manager':
                                value = model_to_dict(Manager.objects.get(pk=value))
                            case 'worker' | 'worker_conversion' | 'worker_retention':
                                print(key, value)
                                value = model_to_dict(Worker.objects.get(pk=value))

                        result['data'][key] = value

                if 'photo' in data:
                    print('dsadasdasdasdasdasdasdasd')
                    print(data['photo'])

            else:
                result['description'] = "Mode not recognized"
        else:
            result['description'] = "Value «Mode» not set"

        return Response(result)


