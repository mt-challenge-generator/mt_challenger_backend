import random
import re
from django.db import transaction
from django.http import JsonResponse,HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from evaluator.models import Testset, TestItem, Phenomenon, Rule, Language, Langpair, Template, TemplatePosition, \
    Distractor, Report, Translation
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

    def retrieve(self, request, pk=None):
        queryset = TestItem.objects.filter(testset__id=pk)
        test_items = [
            TestItemSerializer(x, context={"request": request}).data for x in queryset
        ]
        return Response(test_items)

class TestItemViewSet(viewsets.ModelViewSet):
    queryset = TestItem.objects.all()
    serializer_class = TestItemSerializer
    source_language = None
    target_language = None  
    @action(detail=False, methods=['post'])
    def filter_test_items(self, request):
        try:
            data = request.data
            global source_language, target_language
            source_language = data.get('source_language', None)
            target_language = data.get('target_language', None)
            categories = data.get('categories', [])
            phenomena = data.get('phenomena', [])
            how_many = data.get('howMany', 0)

            queryset = TestItem.objects.all()

            # Filter by language
            # if source_language:
            #      queryset = queryset.filter(testset__langpair__source_language__code=source_language)
            
            # if target_language:
            #      queryset = queryset.filter(testset__langpair__target_language__code=target_language)
            
            langpair_query = Langpair.objects.all()
            if source_language:
                langpair_query = langpair_query.filter(source_language__code=source_language)
            if target_language:
                langpair_query = langpair_query.filter(target_language__code=target_language)
            
            
            testset_query = Testset.objects.filter(langpair__in=langpair_query)
            
        
            queryset = TestItem.objects.filter(testset__in=testset_query)
        
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

            global source_language, target_language  # Access as global
            # Retrieve the Testset object based on source and target languages
            langpair_query = Langpair.objects.all()
            if source_language:
                langpair_query = langpair_query.filter(source_language__code=source_language)
            if target_language:
                langpair_query = langpair_query.filter(target_language__code=target_language)
            
            testset = Testset.objects.filter(langpair__in=langpair_query).first() 
            # Create a new Template
            new_template = Template.objects.create(
                select=0.0,
                scramble_factor=scrambling_factor,
                testset = testset
            )

            # Create TemplatePositions 
            self.create_template_positions(content, rand_list, new_template)
    
            # Generate the text file content
            text_file_content = self.generate_text_file_content(new_template)
            print("text_file_content" + text_file_content)

            return Response({'template_id': new_template.id, 'text_file_content': text_file_content})
            return Response("text_file_content")
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
        #  try:
                template_positions = TemplatePosition.objects.filter(template=template)
                text_file_content = []
                for position in range(1, len(template_positions)* template.scramble_factor + 1):
                    template_position = template_positions.filter(pos=position).first()
                    if template_position and template_position.test_item:
                        text_file_content.append(f" {template_position.test_item.source_sentence}")
                    else:
                        language = template_positions.first().test_item.testset.langpair.source_language
                        random_distractor = self.get_random_distractor(language)
                        text_file_content.append(f" {random_distractor.text}")
                return '\n'.join(text_file_content)

            # except Exception as e:
            #     return None
            
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

    @transaction.atomic
    def create(self, request):
        reports_data = request.data.get('reports', [])
        try:
            for report_data in reports_data:
                template_id = int(report_data['template'])
                template = Template.objects.get(id=template_id)

                # Create the Report instance
                report = Report.objects.create(
                    template=template,
                    engine=report_data['engine'],
                    engine_type=report_data['engine_type'],
                    comment=report_data['comment']
                )

                content = report_data['content']
                translation_segments = re.split(r'\r\n|\n|\r', content)

                # Get template positions for the current template
                template_positions = TemplatePosition.objects.filter(template=template)

                for position, translation_segment in enumerate(translation_segments, start=1):
                    template_position = template_positions.filter(pos=position).first()
                    if template_position is not None:
                        test_item = template_position.test_item
                        translation = Translation.objects.create(
                            test_item=test_item,
                            report=report,
                            sentence=translation_segment
                        )

            return Response({'message': 'Reports and Translation Objects have been created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return HttpResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer