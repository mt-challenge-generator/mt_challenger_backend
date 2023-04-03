from backend.models import Testset, TestItem, Phenomenon, Bucket, BucketCategory, BucketItem, GenerationRule
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from backend.serializers import TestSetSerializer, TestItemSerializer, PhenomenonSerializer, BucketSerializer, \
    BucketCategorySerializer, BucketItemSerializer, RuleSerializer
from rest_framework.response import Response


class BucketViewSet(viewsets.ModelViewSet):
    queryset = Bucket.objects.all()
    serializer_class = BucketSerializer

    """def retrieve(self, request, pk=None):
        queryset = BucketItem.objects.filter(bucket__id=pk)
        test_items = [BucketItemSerializer(x,context={'request': request}).data for x in queryset]
        return Response(test_items)"""
    # permission_classes = []#[permissions.IsAuthenticated]


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


class BucketItemViewSet(viewsets.ModelViewSet):
    queryset = BucketItem.objects.all()
    serializer_class = BucketItemSerializer
    # permission_classes = []#[permissions.IsAuthenticated]


class PhenomenonViewSet(viewsets.ModelViewSet):
    queryset = Phenomenon.objects.all()
    serializer_class = PhenomenonSerializer
    # permission_classes = []#[permissions.IsAuthenticated]


class BucketCategoryViewSet(viewsets.ModelViewSet):
    queryset = BucketCategory.objects.all()
    serializer_class = BucketCategorySerializer


class RuleViewSet(viewsets.ModelViewSet):
    queryset = GenerationRule.objects.all()
    serializer_class = RuleSerializer
