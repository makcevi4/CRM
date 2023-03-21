import random
import requests

from datetime import date, timedelta

from django.core.files import File as ModelFile
from django.db.models import Q
from django.forms import model_to_dict

from .serializers import *
from .handler import get_choices_list
from .handler import FileHandler


class RandomDataMixin(FileHandler):
    def __init__(self):
        super(RandomDataMixin, self).__init__()

    def random_data(self, mode, **kwargs):
        output = dict()
        # match mode:
        #     case 'user':
        #         response = requests.get('https://randomuser.me/api/').json()
        #         array = response['results'][0]
        #         usertype = kwargs.get('usertype')
        #         data = kwargs.get('data', dict())
        #
        #         # workers_conversion = User.objects.filter(Q(groups__))
        #         # workers_retention = Worker.objects.filter(type='retention')
        #
        #         # Client
        #         if usertype == 'client':
        #             status = data.get('status', random.choice(get_choices_list('clients-statuses')['array'])[0])
        #             image_file = self.download(array['picture']['medium'], array['login']['username'])
        #
        #             output = {
        #                 'name': data.get('name',  f"{array['name']['first']} {array['name']['last']}"),
        #                 'photo': ModelFile(open(image_file, 'rb'), name=image_file.replace('temporary/', '')),
        #                 'birthday': data.get('birthday', date.today() - timedelta(days=array['dob']['age'] * 365)),
        #                 'status': status,
        #                 'project': data.get('project', random.choice(get_choices_list('projects')['array'])[0]),
        #                 'contact_telegram': data.get('telegram', f"tg_{array['login']['username']}"),
        #                 'contact_whatsapp': data.get('whatsapp', f"wa_{array['login']['username']}"),
        #                 'contact_discord': data.get('discord', f"ds_{array['login']['username']}"),
        #                 'contact_phone': data.get('phone', random.randint(111111111, 999999999999)),
        #                 'location_city': data.get('city', array['location']['city']),
        #                 'location_country': data.get('country', array['location']['country']),
        #                 'worker_conversion': data.get('conversion', random.choice(workers_conversion).pk)
        #             }
        #
        #             if status != 'conversion':
        #                 output['worker_retention'] = data.get('conversion', random.choice(workers_retention).pk)
        #
        #         # Manager and Worker
        #         elif usertype == 'manager' or usertype == 'worker':
        #             output['common'] = {
        #                 'username': data.get('username', array['login']['username']),
        #                 'password': data.get('password', array['login']['password'] + array['login']['salt']),
        #                 'first_name': data.get('first_name', array['name']['first']),
        #                 'last_name': data.get('last_name', array['name']['last']),
        #                 'email': data.get('email', array['email']),
        #             }
        #
        #             output['additional'] = {
        #                 'telegram': data.get('telegram', f"tg_{array['login']['username']}")
        #             }
        #
        #             if usertype == 'worker':
        #                 random_manager = True
        #
        #                 output['additional']['type'] = data.get(
        #                     'type', random.choice(get_choices_list('workers-types')['array'])[0]
        #                 )
        #
        #                 manager = data.get('manager_id')
        #                 # managers = Manager.objects.all()
        #
        #                 if manager:
        #                     try:
        #                         # output['additional']['manager_id'] = managers.objects.get(pk=manager)
        #                         random_manager = False
        #                     except:
        #                         pass
        #
        #                 if random_manager:
        #                     if managers and bool(random.randbytes(1)):
        #                         output['additional']['manager'] = random.choice(managers).pk
        #
        #     # Comment
        #     case 'comment':
        #         workers = User.objects.all()
        #         clients = Client.objects.all()
        #
        #         response = requests.get(
        #             'https://baconipsum.com/api/',
        #             params={
        #                 'type': 'all-meat',
        #                 'paras': random.randint(2, 5),
        #                 'start-with-lorem': 1 if bool(random.randbytes(1)) else 0,
        #                 'format': 'text'
        #             }
        #         )
        #
        #         output = {
        #             'client': random.choice(clients).pk,
        #             'worker': random.choice(workers).pk,
        #             'text': response.text
        #         }
        #
        #     # Deposit and Withdraw
        #     case 'deposit' | 'withdraw':
        #         clients = Client.objects.all()
        #
        #         output = {
        #             'client': random.choice(clients).pk,
        #             'sum': random.randint(10, 100),
        #             'description': None if not bool(random.randbytes(1)) else f"random_desc:{str(uuid.uuid4())}"
        #         }

        return output

    @staticmethod
    def format_object(data):
        result = dict()

        for key, value in data.items():
            item_model, item_serializer = None, None

            match key:
                case 'user':
                    item_model = User
                    item_serializer = UserSerializer

                case 'client':
                    item_model = Client
                    item_serializer = ClientSerializer

            if item_model and item_serializer:
                item_object = item_model.objects.get(pk=value)
                serialized_item = item_serializer(item_object)

                value = serialized_item.data

            result[key] = value

        return result



