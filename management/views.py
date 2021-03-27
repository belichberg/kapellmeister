from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .helpers import method_permission_classes
from .serializers import ContainerSerializer, ContainerUpdateSerializer
from .models import Container, Project, Channel
from rest_framework.parsers import JSONParser


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


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

        serialized_data = ContainerUpdateSerializer(data=JSONParser().parse(request), many=True)
        serialized_data.is_valid(raise_exception=True)
        data = serialized_data.validated_data

        project = get_object_or_404(Project, slug=project_slug)
        channel = get_object_or_404(Channel, slug=channel_slug)

        containers = Container.objects.filter(project=project, channel=channel)

        for container in containers.values():

            try:
                data_container = data.pop(data.index([d for d in data if d['slug'] == container['slug']][0]))

                rewrite = False
                for key, value in data_container.items():
                    if container[key] != value:
                        container[key] = value
                        rewrite = True

                if rewrite:
                    new_container = Container(**container)
                    new_container.save()

            except IndexError:
                Container(**container).delete()

        if data:
            for container in data:
                Container.objects.create(
                    project=project,
                    channel=channel,
                    slug=container['slug'],
                    path=container['path'],
                    auth=container['auth'],
                    hash=container['hash']
                )

        updated_containers = Container.objects.filter(project=project, channel=channel)
        serializer = self.serializer_class(updated_containers, many=True)

        return Response(serializer.data)

    @method_permission_classes((IsAdminUser,))
    def delete(self, request, project_slug, channel_slug):
        data = JSONParser().parse(request)

        project = get_object_or_404(Project, slug=project_slug)
        channel = get_object_or_404(Channel, slug=channel_slug)

        Container.objects.filter(project=project, channel=channel, slug=data['slug']).delete()

        containers = Container.objects.filter(project=project, channel=channel)
        serializer = self.serializer_class(containers, many=True)

        return Response(serializer.data)
