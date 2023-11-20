from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response

from evaluator.models import Testset, TestItem, Phenomenon, Rule, Language, Langpair
from evaluator.serializers import (
    TestSetSerializer,
    TestItemSerializer,
    PhenomenonSerializer,
    RuleSerializer,
    LanguageSerializer,
    LangpairSerializer
)


class TestSetViewSet(viewsets.ModelViewSet):
    queryset = Testset.objects.all()
    serializer_class = TestSetSerializer

    # permission_classes = []#[permissions.IsAuthenticated]

    def retrieve(self, request, pk=None):
        queryset = TestItem.objects.filter(testset__id=pk)
        test_items = [
            TestItemSerializer(x, context={"request": request}).data for x in queryset
        ]
        return Response(test_items)


class TestItemViewSet(viewsets.ModelViewSet):
    queryset = TestItem.objects.all()
    serializer_class = TestItemSerializer

    @action(detail=False, methods=['post'])
    def filter_test_items(self, request):
        try:
            data = request.data
            source_language = data.get('source_language', None)
            target_language = data.get('target_language', None)
            categories = data.get('categories', [])
            phenomena = data.get('phenomena', [])
            how_many = data.get('howMany', 0)

            queryset = TestItem.objects.all()

            # Filter by language
            if source_language:
                 queryset = queryset.filter(testset__langpair__source_language__code=source_language)
            
            if target_language:
                 queryset = queryset.filter(testset__langpair__target_language__code=target_language)


            # # Filter by categories
            if categories:
               queryset = queryset.filter(phenomenon__category__name__in=categories)

            # # Filter by phenomena
            if phenomena:
                queryset = queryset.filter(phenomenon__name__in=phenomena)

            # Get the desired fields
            results = queryset.values_list('id', 'source_sentence', 'phenomenon__name', 'phenomenon__category__name')[:how_many]

            # serializer = TestItemSerializer(results, many=True)
            print(results)
            return Response(results)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class PhenomenonViewSet(viewsets.ModelViewSet):
    queryset = Phenomenon.objects.all()
    serializer_class = PhenomenonSerializer
    # permission_classes = []#[permissions.IsAuthenticated]


class RuleViewSet(viewsets.ModelViewSet):
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    
class LangpairViewSet(viewsets.ModelViewSet):
    queryset = Langpair.objects.all()
    serializer_class = LangpairSerializer