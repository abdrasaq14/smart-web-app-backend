from rest_framework import serializers

from core.models import Alert, TransactionHistory


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'alert_id', 'site', 'zone', 'district', 'activity', 'status', 'time']


class TransactionHistorySerializer(serializers.ModelSerializer):

    days = serializers.SerializerMethodField()

    class Meta:
        model = TransactionHistory
        fields = ['id', 'site', 'subscription', 'amount_billed', 'amount_bought', 'days', 'time']

    def get_days(self, obj):
        return obj.duration_days or 0
