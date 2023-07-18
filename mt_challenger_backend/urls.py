from django.urls import include, path
from rest_framework import routers
from django.contrib import admin
import generator.views
import evaluator.views


router = routers.DefaultRouter()
router.register(r"testsets", evaluator.views.TestSetViewSet)
router.register(r"testitems", evaluator.views.TestItemViewSet)
router.register(r"buckets", generator.views.BucketViewSet)
router.register(r"phenomena", evaluator.views.PhenomenonViewSet)
router.register(r"bucket-categories", generator.views.BucketCategoryViewSet)
router.register(r"bucket-items", generator.views.BucketItemViewSet)
router.register(r"rules", evaluator.views.RuleViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    # path("api/", include(router.urls)),
    # path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
