from rest_framework import serializers


class WidgetsSerializer(serializers.Serializer):
    total_revenue = serializers.FloatField()
