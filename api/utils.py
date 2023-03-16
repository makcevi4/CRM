import json
import os
import random
import requests

from datetime import date, timedelta

from django.contrib import admin
from django.core.files import File

from CRM.settings import BASE_DIR


def local_file(mode, filename, path=None, filetype='json', encoding='utf-8', data=None):
    filepath = f"{path}/{filename}.{filetype}" if path is not None else f"{filename}.{filetype}"

    match mode:
        case 'write':
            mode = 'w'
        case 'load':
            mode = 'rb'
        case _:
            mode = 'r'

    match filename:
        case 'settings':
            filepath = BASE_DIR / 'settings.json'

    with open(filepath, mode, encoding=encoding) as file:
        match mode:
            case 'w':
                if filetype == 'json':
                    json.dump(data, file)
                else:
                    file.write(data)

            case 'r':
                if filetype == 'json':
                    return json.load(file)
                else:
                    return file.read()


def get_choices_list(mode, default=None):
    array, result = dict(), {'default': None, 'array': list()}
    data = local_file('read', 'settings')['choices'][mode]

    if type(data) == list:
        for item in data:
            array[item] = item.capitalize()

            if default and default == item:
                result['default'] = (item, item.capitalize())

    elif type(data) == dict:
        for key, value in data.items():
            array[key] = value.capitalize()

            if default and default == key:
                result['default'] = (key, value.capitalize())

    result['array'] = [(key, value) for key, value in array.items()]

    return result


def download_file(url, filename, filetype=None, filepath='default'):
    filepath = 'temporary' if filepath == 'default' else filepath
    response = requests.get(url)

    if filetype is None:
        filetype = url.split('/')[-1].split('.')[-1]

    file = f"{filename}.{filetype}"\

    with open(f"{filepath}/{file}", 'wb') as image_file:
        image_file.write(response.content)

    return f"{filepath}/{file}"


def remove_file(file):
    # print(file)
    # file.close()
    return os.remove(f"{BASE_DIR}/{file}")


def get_random_data(mode, **kwargs):
    output = dict()

    match mode:
        case 'user':
            response = requests.get('https://randomuser.me/api/').json()
            array = response['results'][0]
            usertype = kwargs.get('usertype')
            data = kwargs.get('data', dict())
            workers = kwargs.get('workers')

            # Client
            if usertype == 'client':
                status = data.get('status', random.choice(get_choices_list('clients-statuses')['array'])[0])
                image_file = download_file(array['picture']['medium'], array['login']['username'])

                output = {
                    'name': data.get('name',  f"{array['name']['first']} {array['name']['last']}"),
                    'photo': File(open(image_file, 'rb')),
                    'birthday': data.get('birthday', date.today() - timedelta(days=array['dob']['age'] * 365)),
                    'status': status,
                    'project': data.get('project', random.choice(get_choices_list('projects')['array'])[0]),
                    'contact_telegram': data.get('telegram', f"tg_{array['login']['username']}"),
                    'contact_whatsapp': data.get('whatsapp', f"wa_{array['login']['username']}"),
                    'contact_discord': data.get('discord', f"ds_{array['login']['username']}"),
                    'contact_phone': data.get('phone', random.randint(111111111, 999999999999)),
                    'location_city': data.get('city', array['location']['city']),
                    'location_country': data.get('country', array['location']['country']),
                    'worker_conversion': data.get('conversion', random.choice(workers['conversion']).id)
                }

                if status != 'conversion':
                    output['worker_retention'] = data.get('conversion', random.choice(workers['conversion']).id)

            # Manager and Worker
            elif usertype == 'manager' or usertype == 'worker':
                output['common'] = {
                    'username': data.get('username', array['login']['username']),
                    'password': data.get('password', array['login']['password'] + array['login']['salt']),
                    'first_name': data.get('first_name', array['name']['first']),
                    'last_name': data.get('last_name', array['name']['last']),
                    'email': data.get('email', array['email']),
                }

                output['additional'] = {
                    'telegram': data.get('telegram', f"tg_{array['login']['username']}")
                }

                if usertype == 'worker':
                    random_manager = True

                    output['additional']['type'] = data.get(
                        'type', random.choice(get_choices_list('workers-types')['array'])[0]
                    )

                    manager = data.get('manager_id')
                    managers = kwargs.get('managers')

                    if manager:
                        try:
                            output['additional']['manager_id'] = managers.objects.get(pk=manager)
                            random_manager = False
                        except:
                            pass

                    if random_manager:
                        if managers and bool(random.randbytes(1)):
                            output['additional']['manager'] = random.choice(managers).id

        # Deposit and Withdraw
        case 'deposit' | 'withdraw':
            pass

    return output


def recognition_connection_table():
    pass


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper



