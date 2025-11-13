from rest_framework import serializers

class CustomResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    status = serializers.IntegerField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.JSONField(), required=False)
    errors = serializers.DictField(child=serializers.CharField(), required=False)
