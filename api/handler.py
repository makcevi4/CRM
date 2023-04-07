import os
import json
import requests

from django.contrib import admin

from CRM.settings import BASE_DIR


class FileHandler:
    @staticmethod
    def local(mode, filename, path=None, filetype='json', encoding='utf-8', data=None):
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

    @staticmethod
    def download(url, filename, filetype=None, filepath='default'):
        filepath = 'tmp' if filepath == 'default' else filepath
        response = requests.get(url)

        if filetype is None:
            filetype = url.split('/')[-1].split('.')[-1]

        file = f"{filename}.{filetype}"

        with open(f"{filepath}/{file}", 'wb') as image_file:
            image_file.write(response.content)

        return f"{filepath}/{file}"

    @staticmethod
    def remove_temporary_file(obj):
        try:
            os.remove(f"{BASE_DIR}/{obj.file.name}")
        except PermissionError:
            pass


def get_choices_list(mode, default=None, json_parse=False):
    array, result = dict(), {'default': None, 'array': list()}
    data = FileHandler.local('read', 'settings')['choices'][mode]

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

    result['array'] = data if json_parse else [(key, value) for key, value in array.items()]

    return result


def custom_titled_filter(title):
    class Wrapper(admin.FieldListFilter):
        def __new__(cls, *args, **kwargs):
            instance = admin.FieldListFilter.create(*args, **kwargs)
            instance.title = title
            return instance
    return Wrapper