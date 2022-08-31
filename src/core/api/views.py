from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

from core.api.serializers import WidgetsSerializer

# Create your views here.


class WidgetsApiView(ListAPIView):
    """
    Lists all the projects and allows to create a project as well.
    """
    serializer_class = WidgetsSerializer

    def get(self, request, **kwargs):
        serializer = self.get_serializer_class()({'total_revenue': 1232.324})
        return Response(serializer.data, status=status.HTTP_200_OK)
