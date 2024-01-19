from rest_framework import serializers
from evaluator.models import Testset, Rule, TestItem, Phenomenon, Langpair, Language, Distractor, Report


class TestSetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Testset
        fields = "__all__"

class TestItemSerializer(serializers.HyperlinkedModelSerializer):
    rule = serializers.SerializerMethodField("get_linked_rule")

    def get_linked_rule(self, item):
        rule = Rule.objects.filter(pk=item.id)
        if len(rule) == 0:
            return None
        else:
            serialized_rule = RuleSerializer(rule[0], context=self.context)
            return serialized_rule.data

    class Meta:
        model = TestItem
        fields = "__all__"

class PhenomenonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Phenomenon
        # TODO: serialize the category of the phenomenon
        fields = ["name"]


class RuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rule
        fields = "__all__"

class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
        fields='__all__'
        
class LangpairSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Langpair
        fields='__all__'

class DistractorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Distractor
        fields='__all__' 
        
class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields='__all__'