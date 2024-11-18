from rest_framework import serializers
from evaluator.models import Testset, Rule, TestItem, Phenomenon, Langpair, Language, Distractor, Report,Translation,Category, Template


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

class PhenomenonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phenomenon
        fields = ['name']

class CategorySerializer(serializers.ModelSerializer):
    phenomenon_set = PhenomenonSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['name', 'phenomenon_set']

class RuleSerializer(serializers.ModelSerializer):
    source_sentence = serializers.CharField(source='item.source_sentence', read_only=True)
    target_sentence = serializers.SerializerMethodField()

    class Meta:
        model = Rule
        fields = ['id', 'string', 'regex', 'positive', 'source_sentence', 'target_sentence']

    def get_target_sentence(self, obj):
        translation = Translation.objects.filter(test_item=obj.item).first()
        return translation.sentence if translation else ""

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
    language_direction = serializers.SerializerMethodField()

    def get_language_direction(self, obj):
        try:
            source_language = obj.template.testset.langpair.source_language.code.upper()
            target_language = obj.template.testset.langpair.target_language.code.upper()
            return f"{source_language} \u2192 {target_language}"
        except AttributeError:
            return None
        
    class Meta:
        model = Report
        fields='__all__'
        
class TranslationSerializer(serializers.ModelSerializer):
    source_sentence = serializers.CharField(source='test_item.source_sentence')
    category_name = serializers.CharField(source='test_item.phenomenon.category.name')
    phenomenon_name = serializers.CharField(source='test_item.phenomenon.name')

    class Meta:
        model = Translation
        fields = ['id', 'label', 'sentence', 'source_sentence', 'category_name', 'phenomenon_name']      
        
class TemplateWithReportSerializer(serializers.ModelSerializer):
    engines = serializers.SerializerMethodField()
    language_direction = serializers.SerializerMethodField()
    
    class Meta:
        model = Template
        fields = ['id', 'legacy_id', 'name', 'select', 'scramble_factor', 'created_time', 'engines', "language_direction"]

    def get_engines(self, obj):
        reports = Report.objects.filter(template=obj)
        # Return a list of dictionaries with both id and engine name
        return [{'reportid': report.id, 'engine_name': report.engine} for report in reports]
   
    def get_language_direction(self, obj):
        try:
            source_language = obj.testset.langpair.source_language.code.upper()
            target_language = obj.testset.langpair.target_language.code.upper()
            return f"{source_language} \u2192 {target_language}"
        except AttributeError:
            return None