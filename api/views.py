from rest_framework import generics, views
from rest_framework.response import Response
from django.apps import apps

from .utils import *
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
                        serializer = ManagerSerializer

                        array = get_random_data('user', usertype=mode, data=request.data)
                        userdata, data = array['common'], array['additional']

                    case 'worker':
                        serializer = WorkerSerializer

                        array = get_random_data('user', usertype=mode, data=request.data)
                        userdata, data = array['common'], array['additional']

                    case 'client':
                        serializer = ClientSerializer

                        data = get_random_data('user', usertype=mode, data=request.data)

                    case 'comment':
                        serializer = CommentSerializer

                        data = get_random_data(mode)

                    case 'deposit':
                        serializer = DepositSerializer

                        data = get_random_data(mode)

                    case 'withdraw':
                        serializer = WithdrawSerializer

                        data = get_random_data(mode)

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
                    # serialized.save()

                    print(apps.get_model('api', 'ManagerSerializer'))

                    result['status'] = True
                    result['description'] = f"{mode.capitalize()} has been added"
                    result['data'] = dict()

                if 'photo' in data:
                    remove_file(data['photo'])

            else:
                result['description'] = "Mode not recognized"
        else:
            result['description'] = "Value «Mode» not set"

        return Response(result)


