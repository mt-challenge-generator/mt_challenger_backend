from rest_framework import serializers
from backend.models import Testset, TestItem, Phenomenon, Rule, Bucket, BucketCategory, BucketItem
import json


class TestSetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Testset
        fields = '__all__'


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


class TestItemSerializer(serializers.HyperlinkedModelSerializer):
    rule = serializers.SerializerMethodField('get_linked_rule')

    def get_linked_rule(self, item):
        rule = Rule.objects.filter(pk=item.id)
        if len(rule) == 0:
            return None
        else:
            serialized_rule = RuleSerializer(rule[0], context=self.context)
            return serialized_rule.data

    class Meta:
        model = TestItem
        fields = '__all__'


class PhenomenonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Phenomenon
        fields = ['name']


class BucketCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BucketCategory
        fields = '__all__'


class RuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rule
        fields = '__all__'
