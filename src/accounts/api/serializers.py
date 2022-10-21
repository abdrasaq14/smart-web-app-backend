from rest_framework import serializers

from accounts.models import User
from core.api.serializers import CompanySerializer


class UserSerializer(serializers.ModelSerializer):
    companies = CompanySerializer(many=True)
    class Meta:
        model = User
        fields = ('id', 'access_level', 'email', 'first_name', 'last_name', 'companies', 'employee_id', 'time')
