import random
import requests

from datetime import date, timedelta

from django.apps import apps
from django.core.files import File as ModelFile

from .serializers import *
from .permissions import *
from .handler import FileHandler, get_choices_list


class RandomDataMixin(FileHandler):
    def __init__(self):
        super(RandomDataMixin, self).__init__()

    def random_data(self, mode, **kwargs):
        data, response = kwargs.get('data', dict()), {'status': True, 'description': None, 'data': dict}
        random_data = requests.get('https://randomuser.me/api/').json()['results'][0]

        match mode:
            # Manager
            case 'manager':
                response['data'] = {
                    'username': data.get('username', random_data['login']['username']),
                    'password': data.get('password', random_data['login']['password'] + random_data['login']['salt']),
                    'first_name': data.get('first_name', random_data['name']['first']),
                    'last_name': data.get('last_name', random_data['name']['last']),
                    'email': data.get('email', random_data['email']),
                    'telegram': data.get('telegram', f"tg_{random_data['login']['username']}"),
                    'role': get_choices_list('staff-roles', default=mode)['default'][0]
                }

                response['data']['type'] = f"{mode.capitalize()}s"

            # Worker
            case 'worker':
                manager = self.additional_data('manager', data)
                if type(manager) is str:
                    response['status'] = False
                    response['description'] = manager
                    return response

                response['data'] = {
                    'username': data.get('username', random_data['login']['username']),
                    'password': data.get('password', random_data['login']['password'] + random_data['login']['salt']),
                    'first_name': data.get('first_name', random_data['name']['first']),
                    'last_name': data.get('last_name', random_data['name']['last']),
                    'email': data.get('email', random_data['email']),
                    'telegram': data.get('telegram', f"tg_{random_data['login']['username']}"),
                    'role': get_choices_list('staff-roles', default=mode)['default'][0],
                    'manager': manager
                }

                response['data']['type'] = random.choice(
                    list(get_choices_list('workers-types', json_parse=True)['array'].keys())
                ).capitalize()

            # Client
            case 'client':
                worker_conversion, worker_retention = None, None

                status = self.additional_data('status', data)
                if status not in get_choices_list("clients-statuses", json_parse=True)['array']:
                    response['status'] = False
                    response['description'] = status
                    return response

                worker_conversion = self.additional_data('worker_conversion', data)

                if type(worker_conversion) is str:
                    response['status'] = False
                    response['description'] = worker_conversion
                    return response

                if status != 'conversion':
                    worker_retention = self.additional_data('worker_retention', data)
                    if type(worker_retention) is str:
                        response['status'] = False
                        response['description'] = worker_retention
                        return response

                image_file = self.download(random_data['picture']['medium'], random_data['login']['username'])

                response['data'] = {
                    'name': data.get('name', f"{random_data['name']['first']} {random_data['name']['last']}"),
                    'photo': ModelFile(open(image_file, 'rb'), name=image_file.replace('temporary/', '')),
                    'birthday': data.get('birthday', date.today() - timedelta(days=random_data['dob']['age'] * 365)),
                    'status': status,
                    'project': data.get('project', random.choice(get_choices_list('projects')['array'])[0]),
                    'contact_telegram': data.get('telegram', f"tg_{random_data['login']['username']}"),
                    'contact_whatsapp': data.get('whatsapp', f"wa_{random_data['login']['username']}"),
                    'contact_discord': data.get('discord', f"ds_{random_data['login']['username']}"),
                    'contact_phone': data.get('phone', random.randint(111111111, 999999999999)),
                    'location_city': data.get('city', random_data['location']['city']),
                    'location_country': data.get('country', random_data['location']['country']),
                    'worker_conversion': worker_conversion,
                    'worker_retention': worker_retention
                }

            # Comment
            case 'comment':
                worker = self.additional_data('random_worker', data)
                if type(worker) is str:
                    response['status'] = False
                    response['description'] = worker
                    return response

                client = self.additional_data('client', data)
                if type(client) is str:
                    response['status'] = False
                    response['description'] = client
                    return response

                text_data = requests.get(
                    'https://baconipsum.com/api/',
                    params={
                        'type': 'all-meat',
                        'paras': random.randint(2, 5),
                        'start-with-lorem': 1 if bool(random.randbytes(1)) else 0,
                        'format': 'text'
                    }
                )

                response['data'] = {
                    'client': client,
                    'worker': worker,
                    'text': text_data.text
                }

            # Deposit and Withdraw
            case 'deposit' | 'withdraw':
                client = self.additional_data('client', data)
                if type(client) is str:
                    response['status'] = False
                    response['description'] = client
                    return response

                response['data'] = {
                    'client': client,
                    'sum': random.randint(10, 100),
                    'description': None if not bool(random.randbytes(1)) else f"random_desc:{str(uuid.uuid4())}"
                }

        return response

    @staticmethod
    def additional_data(mode, data):
        result = None

        match mode:
            case 'status':
                status = data.get('status')

                if status:
                    statuses = get_choices_list('clients-statuses', json_parse=True)['array']
                    status = random.choice(list(statuses.keys()))

                else:
                    statuses = get_choices_list('clients-statuses')['array']
                    status = random.choice(statuses)[0]

                result = status

            case 'manager' | 'worker_conversion' | 'worker_retention':
                group, message_single, message_plural = None, None, None

                match mode:
                    case 'manager':
                        group = f"{mode}s"

                        message_single = f"{mode} not found"
                        message_plural = f"No {mode}s"

                    case 'worker_conversion' | 'worker_retention':
                        values = mode.split('_')
                        mode, group = values[0], values[-1]

                        message_single = f"{mode} not found"
                        message_plural = f"No {group} {mode}s"

                item = data.get(mode)

                if item:
                    try:
                        item = User.objects.get(
                            Q(role=mode) &
                            Q(groups__name=group.capitalize()) &
                            (Q(pk=item) if item.isdigit() else Q(username=item))
                        ).pk

                    except User.DoesNotExist:
                        return message_single.capitalize()
                else:
                    items = User.objects.filter(groups__name=group.capitalize())

                    if len(items):
                        item = random.choice(items).pk
                    else:
                        if mode == 'worker' and group == 'retention':
                            item = None
                        else:
                            return message_plural

                result = item

            case 'random_worker':
                worker = data.get('worker')

                if worker:
                    try:
                        worker = User.objects.get(
                            Q(pk=worker) if worker.isdigit() else Q(username=worker) &
                            Q(role='worker') &
                            (Q(groups__name='Conversion') | Q(groups__name='Retention'))
                        )

                    except User.DoesNotExist:
                        return "Worker not found"

                else:
                    workers = User.objects.filter(
                        Q(role='worker') &
                        (Q(groups__name='Conversion') | Q(groups__name='Retention'))
                    )

                    if len(workers):
                        worker = random.choice(workers).pk
                    else:
                        return "No workers"

                result = worker

            case 'client':
                client = data.get('client')

                if client:
                    try:
                        client = Client.objects.get(
                            Q(pk=client) if client.isdigit() else Q(name=client)
                        )
                    except Client.DoesNotExist:
                        return "Client not found"

                else:
                    clients = Client.objects.all()

                    if len(clients):
                        client = random.choice(clients).pk
                    else:
                        return "No clients"

                result = client

        return result
    # @staticmethod
    # def format_object(data):
    #     result = dict()
    #
    #     for key, value in data.items():
    #         item_model, item_serializer = None, None
    #
    #         match key:
    #             case 'user':
    #                 item_model = User
    #                 item_serializer = UserSerializer
    #
    #             case 'client':
    #                 item_model = Client
    #                 item_serializer = ClientSerializer
    #
    #         if item_model and item_serializer:
    #             item_object = item_model.objects.get(pk=value)
    #             serialized_item = item_serializer(item_object)
    #
    #             value = serialized_item.data
    #
    #         result[key] = value
    #
    #     return result


class ViewSetMixin:
    def recognize_serializer(self, model, action, user):
        serializer = None

        match model:
            case 'worker':
                serializer = WorkerSerializer

                match action:
                    case 'list' | 'retrieve':
                        if user == 'manager':
                            serializer = ManagerWorkersSerializer
                    case 'create':
                        serializer = WorkerCreationSerializer
        print(f"recognize_serializer:\naction:{action}\nserializer:{serializer}")
        return serializer

    def recognize_permissions(self, model, action):
        permissions = None

        match model:
            case 'worker':
                permissions = [IsAdmin | IsManager]

                print(action)
                match action:
                    case 'retrieve':
                        permissions = [IsAdmin | IsCurrentUser | IsCurrentManager]
                    case 'create' | 'destroy':
                        permissions = [IsAdmin]
                    case 'update' | 'partial_update':
                        permissions = [IsAdmin | IsCurrentUser]

        print(f"recognize_permissions:\naction:{action}\npermissions:{permissions}")
        return permissions


class RendererMixin:
    @staticmethod
    def get_error(data):
        detail = data.get('detail')

        if detail:
            result = detail
        else:
            i, result = 1, str()

            for field, error in data.items():
                result += f"{field} - {error[0]} "

        return result

    @staticmethod
    def get_item(request, **kwargs):
        result = 'item'

        roles_list = list(get_choices_list('staff-roles', json_parse=True)['array'].keys())
        models_list = [model.__name__.lower() for model in apps.get_models()]
        triggers = roles_list + models_list

        mode = [item for item in request.path.split('/') if item != ''][1]

        if mode.endswith('s'):
            mode = mode[:-1]

        if mode in triggers:
            match request.method:
                case 'GET':
                    result = mode if kwargs.get('pk') else f"{mode}s"
                case _:
                    result = mode

        return result
