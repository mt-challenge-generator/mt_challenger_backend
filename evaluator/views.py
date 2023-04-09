from rest_framework import viewsets
from rest_framework.response import Response

from evaluator.models import Testset, TestItem, Phenomenon, Rule
from evaluator.serializers import TestSetSerializer, TestItemSerializer, PhenomenonSerializer, RuleSerializer


class TestSetViewSet(viewsets.ModelViewSet):
    queryset = Testset.objects.all()
    serializer_class = TestSetSerializer

    # permission_classes = []#[permissions.IsAuthenticated]

    def retrieve(self, request, pk=None):
        queryset = TestItem.objects.filter(testset__id=pk)
        test_items = [TestItemSerializer(x, context={'request': request}).data for x in queryset]
        return Response(test_items)


class TestItemViewSet(viewsets.ModelViewSet):
    queryset = TestItem.objects.all()
    serializer_class = TestItemSerializer

    # permission_classes = []#[permissions.IsAuthenticated]


class PhenomenonViewSet(viewsets.ModelViewSet):
    queryset = Phenomenon.objects.all()
    serializer_class = PhenomenonSerializer
    # permission_classes = []#[permissions.IsAuthenticated]


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer
