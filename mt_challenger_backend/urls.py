from django.urls import include, path
from rest_framework import routers
from backend import views

router = routers.DefaultRouter()
router.register(r'testsets', views.TestSetViewSet)
router.register(r'testitems', views.TestItemViewSet)
router.register(r'buckets', views.BucketViewSet)
router.register(r'phenomena', views.PhenomenonViewSet)
router.register(r'bucket-categories', views.BucketCategoryViewSet)
router.register(r'bucket-items', views.BucketItemViewSet)
router.register(r'rules', views.RuleViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]