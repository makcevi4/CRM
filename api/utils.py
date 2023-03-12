import json

from CRM.settings import BASE_DIR


def local_file(mode, filename, path=None, filetype='json', data=None):
    filepath = f"{path}/{filename}.{filetype}" if path is not None else f"{filename}.{filetype}"
    mode = 'w' if mode == 'write' and data is not None else 'r'

    match filename:
        case 'settings':
            filepath = BASE_DIR / 'settings.json'

    with open(filepath, mode) as file:
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
