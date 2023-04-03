from generator.models import Bucket, BucketCategory, BucketItem
from rest_framework import viewsets
from generator.serializers import BucketSerializer, BucketCategorySerializer, BucketItemSerializer


class BucketViewSet(viewsets.ModelViewSet):
    queryset = Bucket.objects.all()
    serializer_class = BucketSerializer

    """def retrieve(self, request, pk=None):
        queryset = BucketItem.objects.filter(bucket__id=pk)
        test_items = [BucketItemSerializer(x,context={'request': request}).data for x in queryset]
        return Response(test_items)"""
    # permission_classes = []#[permissions.IsAuthenticated]


class BucketItemViewSet(viewsets.ModelViewSet):
    queryset = BucketItem.objects.all()
    serializer_class = BucketItemSerializer
    # permission_classes = []#[permissions.IsAuthenticated]


class BucketCategoryViewSet(viewsets.ModelViewSet):
    queryset = BucketCategory.objects.all()
    serializer_class = BucketCategorySerializer


