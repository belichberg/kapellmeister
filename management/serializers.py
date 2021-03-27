from rest_framework import serializers


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


class ContainerUpdateSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        return instance

    def to_internal_value(self, data):
        slug = data.get('slug', None)
        hash_data = data.get('digest', None)
        auth_data = data.get('auth', None)['auths']

        path = list(auth_data.keys())[0]
        auth = auth_data[path]['auth']

        if slug is None:
            raise serializers.ValidationError(
                'A slug is required field.'
            )

        if hash_data is None:
            raise serializers.ValidationError(
                'A slug is required field.'
            )

        return {
            'slug': slug,
            'hash': hash_data,
            'path': path,
            'auth': auth
        }
