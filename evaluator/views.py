from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
import random 
import json
from django.db import transaction
from evaluator.models import Testset, TestItem, Phenomenon, Rule, Language, Langpair, Template, TemplatePosition,Distractor,Report,Translation
from evaluator.serializers import (
    TestSetSerializer,
    TestItemSerializer,
    PhenomenonSerializer,
    RuleSerializer,
    LanguageSerializer,
    LangpairSerializer,
    ReportSerializer,
    TranslationSerializer
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
            Result = queryset.values_list('id', 'source_sentence', 'phenomenon__name', 'phenomenon__category__name')[:how_many]
            return Response(Result)  
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'])
    def download_text_file(self, request):
        try:
            data = request.data
            content = data.get('content', [])
            scrambling_factor = data.get('scramblingFactor', 1)

            scrambling_factor = int(scrambling_factor)

            if len(content) >= scrambling_factor:
                rand_list = random.sample(range(1, len(content) * scrambling_factor + 1), len(content))
                print(rand_list)
            else:
                print("Error: Not enough items for the given scrambling_factor.")

            
            # Create a new Template
            new_template = Template.objects.create(
                select=0.0,
                scramble_factor=scrambling_factor
            )

            # Create TemplatePositions 
            self.create_template_positions(content, rand_list, new_template)

            # Generate the text file content
            text_file_content = self.generate_text_file_content(new_template)
            print("text_file_content" + text_file_content)

            return Response({'template_id': new_template.id, 'text_file_content': text_file_content})
        except Exception as e:
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            

    def create_template_positions(self, filtered_items, rand_list, template):
        try:
            with transaction.atomic():
                for i, item_data in enumerate(filtered_items):
                    test_item_id = item_data.get('dataPointId', None)
                    test_item = TestItem.objects.get(id=test_item_id)
                    # Create TemplatePosition for each TestItem
                    position = rand_list[i]
                    template_position =   TemplatePosition.objects.create(
                        template=template,
                        test_item=test_item,
                        pos=position
                    )
                    print(template_position)
        except Exception as e:
            print(f"Error creating template positions: {str(e)}")
            
    def generate_text_file_content(self ,template):
            try:
                template_positions = TemplatePosition.objects.filter(template=template).order_by('pos')
                text_file_content = []
                for position in range(1, template_positions.count() + 1):
                    template_position = template_positions.filter(pos=position).first()
                    if template_position and template_position.test_item:
                        text_file_content.append(f" {template_position.test_item.source_sentence}")
                    else:
                        language = template_positions.first().test_item.testset.langpair.source_language
                        random_distractor = self.get_random_distractor(language)
                        text_file_content.append(f" {random_distractor.text}")
                return ', '.join(text_file_content)

            except Exception as e:
                return None
            
    def get_random_distractor(self, language):
        distractors = Distractor.objects.filter(language=language)
        return random.choice(distractors)
            
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
    
class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    def create(self, request):
        reports_data = request.data.get('reports', [])
        
        created_reports = []
        with transaction.atomic():
            for report_data in reports_data:
                serializer = self.get_serializer(data=report_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                created_report = serializer.instance
                self.create_translation(created_report.id)  # Call create_translation with report ID
                print(report_data)
                created_reports.append(serializer.data)

        return JsonResponse({'reports': created_reports}, status=status.HTTP_201_CREATED)

    def create_translation(self, report_id):
        try:
            report = Report.objects.get(id=report_id)
            template = report.template
            template_positions = TemplatePosition.objects.filter(template=template)

    
            for template_position in template_positions:
                test_item = template_position.test_item
                
                if test_item:
                    # Retrieve the text from the corresponding line of the template
                    text_line = test_item.source_sentence

                    # Create a new Translation instance
                    Translation.objects.create(
                        test_item=test_item,
                        report=report,
                        sentence=text_line
                    )

            return True
        except Exception as e:
            print(f"Error creating translations: {str(e)}")
            return False

    def get_reports(request):
        if request.method == 'GET':
            reports = Report.objects.all()
            serializer = ReportSerializer(reports, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return JsonResponse({'error': 'Method not allowed'}, status=405)

class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer