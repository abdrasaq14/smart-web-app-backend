from rest_framework import serializers

from core.models import ActivityLog, Alert, EventLog, Site, TransactionHistory, UserLog


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'alert_id', 'site', 'zone', 'district', 'activity', 'status', 'time']


class AlertSerializer(ActivityLogSerializer):
    class Meta(ActivityLogSerializer.Meta):
        model = Alert


class EventLogSerializer(ActivityLogSerializer):
    class Meta(ActivityLogSerializer.Meta):
        model = EventLog


class UserLogSerializer(ActivityLogSerializer):
    class Meta(ActivityLogSerializer.Meta):
        model = UserLog
        fields = ActivityLogSerializer.Meta.fields + ['modified_by', 'employee_id', 'email_address']


class TransactionHistorySerializer(serializers.ModelSerializer):

    days = serializers.SerializerMethodField()

    class Meta:
        model = TransactionHistory
        fields = ['id', 'site', 'subscription', 'amount_billed', 'amount_bought', 'days', 'time']

    def get_days(self, obj):
        return obj.duration_days or 0


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'asset_name', 'asset_type', 'asset_co_ordinate', 'asset_capacity',
                  'under_maintenance', 'is_active', 'time']
