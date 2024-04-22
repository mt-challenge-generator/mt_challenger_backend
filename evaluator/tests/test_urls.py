from django.test import SimpleTestCase
from django.urls import reverse, resolve
from evaluator.views import (
    TestSetViewSet,
    TestItemViewSet,
    PhenomenonViewSet,
    RuleViewSet,
    LangpairViewSet,
    ReportViewSet,
    TranslationViewSet
)

class TestUrls(SimpleTestCase):
    def test_testsets_url_resolves(self):
        url = reverse('testset-list')
        self.assertEqual(resolve(url).func.cls, TestSetViewSet)
    
    def test_testitems_url_resolves(self):
        url = reverse('testitem-list')
        self.assertEqual(resolve(url).func.cls, TestItemViewSet)

    def test_phenomena_url_resolves(self):
        url = reverse('phenomenon-list')
        self.assertEqual(resolve(url).func.cls, PhenomenonViewSet)

    def test_rules_url_resolves(self):
        url = reverse('rule-list')
        self.assertEqual(resolve(url).func.cls, RuleViewSet)

    def test_langpairs_url_resolves(self):
        url = reverse('langpair-list')
        self.assertEqual(resolve(url).func.cls, LangpairViewSet)

    def test_reports_url_resolves(self):
        url = reverse('report-list')
        self.assertEqual(resolve(url).func.cls, ReportViewSet)

    def test_translations_url_resolves(self):
        url = reverse('translation-list')
        self.assertEqual(resolve(url).func.cls, TranslationViewSet)