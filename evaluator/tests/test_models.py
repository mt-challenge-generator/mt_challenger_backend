from django.test import TestCase
from evaluator.models import Language, Langpair, Testset, Category, Phenomenon, TestItem, Rule, Template, Report, Translation, TemplatePosition, Distractor

class ModelTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.language = Language.objects.create(code='en', name='English')
        self.category = Category.objects.create(name='Category A')
        self.phenomenon = Phenomenon.objects.create(category=self.category, name='Phenomenon X')
        self.langpair = Langpair.objects.create(source_language=self.language, target_language=self.language)
        self.testset = Testset.objects.create(name='Test Set 1', description='Description 1', langpair=self.langpair)
        self.rule = Rule.objects.create(string='Test string', regex=True, positive=True)
        self.template = Template.objects.create(name='Template 1', select=0.5, scramble_factor=2.0)
        self.report = Report.objects.create(engine='Engine 1', engine_type='Type 1', comment='Report comment 1')
        self.translation = Translation.objects.create(sentence='Translated sentence 1')
        self.test_item = TestItem.objects.create(legacy_id='123', testset=self.testset, phenomenon=self.phenomenon, source_sentence='Test sentence 1', comment='Test comment 1')
        self.template_position = TemplatePosition.objects.create(template=self.template, test_item=self.test_item, pos=1)
        self.distractor = Distractor.objects.create(text='Distractor text 1', language=self.language)

    # Test Model Fields
    def test_language_fields(self):
        self.assertEqual(self.language.code, 'en')
        self.assertEqual(self.language.name, 'English')

    def test_category_fields(self):
        self.assertEqual(self.category.name, 'Category A')

    def test_phenomenon_fields(self):
        self.assertEqual(self.phenomenon.category, self.category)
        self.assertEqual(self.phenomenon.name, 'Phenomenon X')

    def test_langpair_fields(self):
        self.assertEqual(self.langpair.source_language, self.language)
        self.assertEqual(self.langpair.target_language, self.language)

    def test_testset_fields(self):
        self.assertEqual(self.testset.name, 'Test Set 1')
        self.assertEqual(self.testset.description, 'Description 1')
        self.assertEqual(self.testset.langpair, self.langpair)

    # Test Model Methods
    def test_rule_method(self):
        self.assertTrue(self.rule.regex)

    def test_template_method(self):
        self.assertEqual(self.template.get_scramble_factor_display(), '2.0')

    # Test Model Managers
    def test_report_manager(self):
        self.assertEqual(Report.objects.count(), 1)

    # Test Model Relationships
    def test_translation_relationship(self):
        self.assertEqual(self.translation.test_item, self.test_item)

    def test_testitem_relationship(self):
        self.assertEqual(self.test_item.testset, self.testset)

    def test_templateposition_relationship(self):
        self.assertEqual(self.template_position.test_item, self.test_item)

    def test_distractor_relationship(self):
        self.assertEqual(self.distractor.language, self.language)
