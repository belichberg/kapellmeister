from typing import Dict

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import method_permission_classes
from .models import Container, Project, Channel
from .serializers import ContainerSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


def index(request):
    return HttpResponse("Kapellmeister")


class ContainerView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ContainerSerializer

    def get(self, request, project_slug, channel_slug) -> Response:
        project = get_object_or_404(Project, slug=project_slug)
        channel = get_object_or_404(Channel, slug=channel_slug)

        containers = Container.objects.filter(project=project, channel=channel)
        serializer = self.serializer_class(containers, many=True)

        return Response(serializer.data)

    @method_permission_classes((IsAdminUser,))
    def post(self, request, project_slug, channel_slug):
        data: Dict = request.data

        project = get_object_or_404(Project, slug=project_slug)
        channel = get_object_or_404(Channel, slug=channel_slug)

        data["project"] = project
        data["channel"] = channel

        serializer = self.serializer_class(data=data)
        serializer.is_valid()

        return Response(serializer.data)

    @method_permission_classes((IsAdminUser,))
    def delete(self, request, project_slug, channel_slug):
        data = JSONParser().parse(request)

        project = get_object_or_404(Project, slug=project_slug)
        channel = get_object_or_404(Channel, slug=channel_slug)

        Container.objects.filter(
            project=project, channel=channel, slug=data["slug"]
        ).delete()

        containers = Container.objects.filter(project=project, channel=channel)
        serializer = self.serializer_class(containers, many=True)

        return Response(serializer.data)