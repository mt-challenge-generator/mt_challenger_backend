from backend.models import TestSet
from rest_framework import viewsets
from rest_framework import permissions
from backend.serializers import TestSetSerializer


class TestSetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TestSet.objects.all()
    serializer_class = TestSetSerializer
    permission_classes = []#[permissions.IsAuthenticated]

