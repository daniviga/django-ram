from rest_framework import serializers


class FunctionSerializer(serializers.Serializer):
    function = serializers.IntegerField(required=True)
    state = serializers.IntegerField(required=True)


class CabSerializer(serializers.Serializer):
    speed = serializers.IntegerField(required=True)
    direction = serializers.IntegerField(required=True)


class InfraSerializer(serializers.Serializer):
    power = serializers.BooleanField(required=True)
    track = serializers.ChoiceField(choices=('main', 'prog', 'join'),
                                    required=False)
