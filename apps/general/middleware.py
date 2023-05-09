import json
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status


class MiddlewareData(object):

    data = {}

    def __init__(self, field):
        self.field = field
        self.data = {}

    def dispatch(self, request, *args, **kwargs):
        if request.META["CONTENT_TYPE"] == "application/json":
            self.data = json.loads(
                request.body.decode()).get(self.field, None)
        else:
            self.data = request.POST.dict().get(self.field, None)
        if self.data is not None:
            return super().dispatch(request, *args, **kwargs)
        response = Response({'message': f'El campo de {self.field} es requerido'},
                            status=status.HTTP_401_UNAUTHORIZED)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = 'application/json'
        response.renderer_context = {}
        return response
