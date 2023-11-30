import json

from rest_framework import renderers


class CustomRenderer(renderers.JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'exception' in data:
            if type(data['exception']) == list:
                exception = data['exception'][0]
            else:
                exception = data['exception']
        else:
            exception = data if 'ErrorDetail' in str(data) else ''
        if 'status' in data:
            status = data['status'][0] if type(data['status']) == list else data['status']
        else:
            status = renderer_context['response'].status_code
        return json.dumps(
            {
                'message': str(data['message']) if 'message' in data else '',
                'data': data['data'] if 'data' in data else {},
                'exception': {'detail': exception},
                'status': int(status)
            }
        )