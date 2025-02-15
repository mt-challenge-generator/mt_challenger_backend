from django.urls import include, path
from rest_framework import routers
from django.contrib import admin
import generator.views
import evaluator.views
from evaluator.views import (
ReportTranslationsListView,
RulesByTranslationId, 
UpdateRulesView,
TemplateWithReportViewSet, 
CompareReportsView, 
MatchingReportsView,
CategoryTestItemsView,
)

router = routers.DefaultRouter()
router.register(r"testsets", evaluator.views.TestSetViewSet)
router.register(r"testitems", evaluator.views.TestItemViewSet)
router.register(r"buckets", generator.views.BucketViewSet)
router.register(r"phenomena", evaluator.views.PhenomenonViewSet)
router.register(r"categories", evaluator.views.CategoryViewSet)
router.register(r"bucket-categories", generator.views.BucketCategoryViewSet)
router.register(r"bucket-items", generator.views.BucketItemViewSet)
router.register(r"rules", evaluator.views.RuleViewSet)
router.register(r"langpair", evaluator.views.LangpairViewSet)
router.register(r'reports', evaluator.views.ReportViewSet)
router.register(r'translations', evaluator.views.TranslationViewSet)
router.register(r'templates-with-report', TemplateWithReportViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("api/", include(router.urls)),
    path("api/reports/<int:report_id>/translations/", ReportTranslationsListView.as_view(), name='report-translations-list'),
    path("api/translations/<int:translation_id>/rules/", RulesByTranslationId.as_view(), name='rules-by-translation-id'),
    path('api/matching-reports/<int:template_id>/', MatchingReportsView.as_view(), name='matching-reports'),
    path('api/update-rules/', UpdateRulesView.as_view(), name='update-rules'),
    path('api/compare-reports/', CompareReportsView.as_view(), name='compare-reports'),
    path('api/category/<str:category>/test-items/', CategoryTestItemsView.as_view(), name='category-test-items'),
]
