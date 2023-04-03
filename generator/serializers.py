from rest_framework import serializers
from models import Bucket, BucketCategory, BucketItem


class BucketItemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BucketItem
        fields = '__all__'


class BucketSerializer(serializers.HyperlinkedModelSerializer):
    bucket_items = serializers.SerializerMethodField('get_bucket_items')

    def get_bucket_items(self, bucket):
        bucket_items = BucketItem.objects.filter(bucket__id=bucket.id)
        if len(bucket_items) == 0:
            return None
        else:
            serialized_bucket_items = [BucketItemSerializer(x, context=self.context).data for x in bucket_items]
            return serialized_bucket_items

    class Meta:
        model = Bucket
        fields = '__all__'


class BucketCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BucketCategory
        fields = '__all__'


