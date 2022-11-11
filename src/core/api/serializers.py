from rest_framework import serializers
from accounts.models import User
from core.models import ActivityLog, Alert, Company, Device, DeviceTariff, EventLog, Site, TransactionHistory, UserLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'access_level', 'email', 'first_name', 'last_name', 'employee_id', 'time',
                  'phone_number')


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ["id", "name", "company_type", "service_type", "phone_number", "email", "address",
                  "renewal_date", "users"]


class ListCompanySerializer(CompanySerializer):
    users = UserSerializer(many=True)


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
    site = serializers.SlugRelatedField(
        queryset=Site.objects.all(),
        many=False,
        slug_field='id'
    )

    class Meta:
        model = TransactionHistory
        fields = ["id", "site", "subscription", "amount_billed", "amount_bought", "days", "time"]


class ListTransactionHistorySerializer(TransactionHistorySerializer):
    site_name = serializers.SerializerMethodField()

    class Meta(TransactionHistorySerializer.Meta):
        fields = TransactionHistorySerializer.Meta.fields + ["site_name"]

    def get_site_name(self, obj):
        return f"{obj.site.name}"


class DeviceTariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceTariff
        fields = ("id", "name", "price", "daily_availability")


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ["id", "name", "location", "co_ordinate", "company", "company_district", "asset_type",
                  "asset_capacity", "tariff", "linked_at"]

    def create(self, validated_data):
        new_site = Site.objects.create(
            name=validated_data.get('name'),
            company=validated_data.get('company'),
            asset_name=validated_data.get('name'),
            asset_type="Device site",
            asset_co_ordinate="",
            asset_capacity=""
        )

        new_device = Device.objects.create(
            id=validated_data.get('id'),
            name=validated_data.get('name'),
            location=validated_data.get('location'),
            co_ordinate=validated_data.get('co_ordinate'),
            company=validated_data.get('company'),
            company_district=validated_data.get('company_district'),
            asset_type=validated_data.get('asset_type'),
            asset_capacity=validated_data.get('asset_capacity'),
            site=new_site,
            tariff=validated_data.get('tariff')
        )

        return new_device


class ListDeviceSerializer(DeviceSerializer):
    company = CompanySerializer(many=False)
    tariff = DeviceTariffSerializer(many=False)

    class Meta(DeviceSerializer.Meta):
        fields = DeviceSerializer.Meta.fields + ['site']
