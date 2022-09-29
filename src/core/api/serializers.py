from rest_framework import serializers

from core.models import Alert, Site, TransactionHistory


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'alert_id', 'site', 'zone', 'district', 'activity', 'status', 'created_at']


class TransactionHistorySerializer(serializers.ModelSerializer):

    days = serializers.SerializerMethodField()

    class Meta:
        model = TransactionHistory
        fields = ['id', 'site', 'subscription', 'amount_billed', 'amount_bought', 'days', 'created_at']

    def get_days(self, obj):
        return obj.duration_days or 0


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'asset_name', 'asset_type', 'asset_co_ordinate', 'asset_capacity',
                  'under_maintenance', 'is_active', 'created_at']
