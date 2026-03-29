from rest_framework import serializers

class MetaSerializer(serializers.Serializer):
    total = serializers.IntegerField(help_text="Total number of items")
    page = serializers.IntegerField(help_text="Current page number")
    limit = serializers.IntegerField(help_text="Items per page")
    totalPages = serializers.IntegerField(help_text="Total number of pages")

def wrapped_response_serializer(data_serializer=None, many=False, name=None):
    """
    Dynamically creates a serializer that wraps the data_serializer 
    into the standard response format for Swagger documentation.
    """
    fields = {
        'success': serializers.BooleanField(default=True),
        'status': serializers.IntegerField(default=200),
        'message': serializers.CharField(default="Request successful"),
    }

    if data_serializer:
        if many:
            fields['data'] = serializers.ListField(child=data_serializer())
        else:
            fields['data'] = data_serializer()
    else:
        fields['data'] = serializers.DictField(child=serializers.JSONField(), required=False)

    fields['errors'] = serializers.DictField(child=serializers.JSONField(), required=False)
    fields['meta'] = MetaSerializer(required=False)

    class_name = name or f"Wrapped{data_serializer.__name__ if data_serializer else 'Empty'}Response"
    return type(class_name, (serializers.Serializer,), fields)

class CustomResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    status = serializers.IntegerField()
    message = serializers.CharField()
    data = serializers.DictField(child=serializers.JSONField(), required=False)
    errors = serializers.DictField(child=serializers.JSONField(), required=False)
    meta = MetaSerializer(required=False)
