from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        request = renderer_context['request']
        response = renderer_context['response']

        result = {
            'status': False,
            'description': None,
            'data': {}
        }

        match response.status_code:
            case 200:
                custom_data = data.get('status')

                if custom_data is not None:
                    result['status'] = data.get('status')
                    result['description'] = data.get('description')
                    result['data'] = data.get('data')
                else:
                    result['status'] = True
                    result['data'] = data

                    print(renderer_context['request'].method)

                    match request.method:
                        case 'GET':
                            pk = renderer_context['kwargs'].get('pk')

                            result['description'] = f"Item{'' if pk else 's'} received successfully"

                        case 'PUT' | 'PATCH':
                            if request.data:
                                i = 1
                                items = [request.data.keys()[0]] \
                                    if len(request.data.keys()) < 1 \
                                    else [i for i in request.data.keys()]

                                description = "Success updated: "

                                for item in items:
                                    description += f"{item}, " if i < len(items) else item

                                    i += 1

                                result['description'] = description
                            else:
                                result['description'] = "Nothing has been updated"




            case _:
                result['description'] = data.get('detail')

        data = result

        return super(ApiRenderer, self).render(data, accepted_media_type, renderer_context)