from rest_framework import serializers

from .models import Container


class ContainerSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):

        return {
            'slug': instance.slug,
            'digest': instance.hash,
            'auth': {
                'auths': {
                    instance.path: {
                        'auth': instance.auth
                    }
                }
            },
            'parameters': {
                'name': instance.slug,
                'image': '',
                'environment': []
            }
        }

    def to_internal_value(self, data):

        slug = data.get('slug', None)
        hash_data = data.get('digest', None)
        auth_data = data.get('auth', None)['auths']

        path = list(auth_data.keys())[0]
        auth = auth_data[path]['auth']

        container, created = Container.objects.get_or_create(
            slug=slug,
            defaults={
                'path': path,
                'auth': auth,
                'hash': hash_data,
            }
        )

        return container

    def update(self, instance, validated_data):
        pass
