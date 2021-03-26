from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
# from .models import
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser


class Health(APIView):

    def get(self, request):
        return Response({"status": "ok"})

