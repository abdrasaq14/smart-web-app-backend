from rest_framework import serializers

from core.models import ActivityLog, Alert, Company, Device, DeviceTariff, EventLog, Site, TransactionHistory, UserLog


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "company_type", "service_type", "phone_number", "email", "address",
                  "renewal_date", "users"]


class SiteSerializer(serializers.ModelSerializer):
    company = CompanySerializer(many=False)

    class Meta:
        model = Site
        fields = ["id", "name", "asset_name", "asset_type", "asset_co_ordinate", "asset_capacity",
                  "under_maintenance", "is_active", "time", "company"]


class ActivityLogSerializer(serializers.ModelSerializer):
    site = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field='name'
    )

    class Meta:
        model = ActivityLog
        fields = ["id", "alert_id", "site", "zone", "district", "activity", "status", "time"]


class AlertSerializer(ActivityLogSerializer):
    class Meta(ActivityLogSerializer.Meta):
        model = Alert


class EventLogSerializer(ActivityLogSerializer):
    class Meta(ActivityLogSerializer.Meta):
        model = EventLog


class UserLogSerializer(ActivityLogSerializer):
    class Meta(ActivityLogSerializer.Meta):
        model = UserLog
        fields = ActivityLogSerializer.Meta.fields + [
            "modified_by",
            "employee_id",
            "email_address",
        ]


class TransactionHistorySerializer(serializers.ModelSerializer):

    days = serializers.SerializerMethodField()
    site = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field='name'
    )

    class Meta:
        model = TransactionHistory
        fields = ["id", "site", "subscription", "amount_billed", "amount_bought", "days", "time"]

    def get_days(self, obj):
        return obj.duration_days or 0


class DeviceTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceTariff
        fields = ("id", "name", "price", "daily_availability")


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "name", "location", "co_ordinate", "company", "asset_type",
                  "asset_capacity", "tariff", "site", "linked_at"]


class ListDeviceSerializer(DeviceSerializer):
    company = CompanySerializer(many=False)
    tariff = DeviceTariffSerializer(many=False)
