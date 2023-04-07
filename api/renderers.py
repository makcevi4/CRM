from rest_framework.renderers import JSONRenderer
from .utils import RendererMixin


class ApiRenderer(JSONRenderer, RendererMixin):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = renderer_context['request']
        response = renderer_context['response']
        kwargs = renderer_context['kwargs']

        result = {
            'status': False,
            'description': None,
            'data': {}
        }

        match response.status_code:
            case 200:
                status = data.get('status')

                if status is not None and type(status) is bool:
                    result['status'] = data.get('status')
                    result['description'] = data.get('description')
                    result['data'] = data.get('data')
                else:
                    result['status'] = True
                    result['data'] = data

                    match request.method:
                        case 'GET':
                            item = self.get_item(request, **kwargs)
                            result['description'] = f"{item.capitalize()} received successfully"

                        case 'PUT' | 'PATCH':
                            if request.data:
                                item, i = self.get_item(request, **kwargs), 1

                                updates = [request.data.keys()[0]] \
                                    if len(request.data.keys()) < 1 \
                                    else [i for i in request.data.keys()]

                                description = f"New updates for {item}: "

                                for update in updates:
                                    description += f"{update}, " if i < len(updates) else update

                                    i += 1

                                result['description'] = description
                            else:
                                result['description'] = "Nothing has been updated"

            case 201:
                item = self.get_item(request, **kwargs)

                result['status'] = True
                result['description'] = f"{item.capitalize()} has been added successfully"
                result['data'] = data

            case 204:
                item = self.get_item(request, **kwargs)

                result['status'] = True
                result['description'] = f"{item.capitalize()} has been deleted successfully"

            case _:
                result['description'] = self.get_error(data)

        data = result

        return super(ApiRenderer, self).render(data, accepted_media_type, renderer_context)