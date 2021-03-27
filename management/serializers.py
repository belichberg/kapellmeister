import json

from rest_framework import serializers

from management.models import Container


class ContainerSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            "slug": instance.slug,
            "digest": instance.hash,
            "auth": {"auths": {instance.path: {"auth": instance.auth}}},
            "parameters": {"name": instance.slug, "image": "", "environment": []},
        }

    def to_internal_value(self, data):
        slug = data.get("slug", None)
        hash_data = data.get("digest", None)
        auth_data = data.get("auth", None)["auths"]
        parameters = json.dumps(data.get("parameters", None))
        project = data.get("project", None)
        channel = data.get("channel", None)

        path = list(auth_data.keys())[0]
        auth = auth_data[path]["auth"]

        if slug is None:
            raise serializers.ValidationError("A slug is required field.")

        if hash_data is None:
            raise serializers.ValidationError("A digest is required field.")

        if parameters is None:
            raise serializers.ValidationError("A parameters is required field.")

        container, created = Container.objects.update_or_create(
            project=project,
            channel=channel,
            slug=slug,
            defaults={
                "hash": hash_data,
                "path": path,
                "auth": auth,
                "parameters": parameters,
            },
        )

        return container
