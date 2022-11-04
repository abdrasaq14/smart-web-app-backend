from rest_framework import serializers

from accounts.models import User
from core.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "company_type", "service_type", "phone_number", "email", "address",
                  "renewal_date"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'access_level', 'email', 'first_name', 'last_name', 'companies', 'employee_id',
                  'time', 'phone_number', 'companies')


class ListUserSerializer(UserSerializer):
    companies = CompanySerializer(many=True)
