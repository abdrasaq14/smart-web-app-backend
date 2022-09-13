from rest_framework import serializers

from core.models import Alert


class WidgetsSerializer(serializers.Serializer):
    total_revenue = serializers.FloatField()


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'alert_id', 'site', 'zone', 'district', 'activity', 'status', 'time']
