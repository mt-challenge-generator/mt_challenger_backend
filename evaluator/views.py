import random , logging ,re
import pandas as pd
from scipy.stats import norm
import numpy as np
from django.db import transaction
from django.db.models import Prefetch
from rest_framework.generics import ListAPIView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from evaluator.models import Testset, TestItem, Category,Phenomenon, Rule, Language, Langpair, Template, TemplatePosition, \
    Distractor, Report, Translation
from evaluator.serializers import (
    TestSetSerializer,
    TestItemSerializer,
    PhenomenonSerializer,
    CategorySerializer,
    RuleSerializer,
    LanguageSerializer,
    LangpairSerializer,
    ReportSerializer,
    TranslationSerializer,
    TemplateWithReportSerializer,
    TestItemWithTranslationsSerializer,
    FilteredTestItemSerializer
)
from django.contrib.sessions.models import Session


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
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
    filtered_items = [] 

    @action(detail=False, methods=['post'])
    def filter_test_items(self, request):
        try:
            data = request.data
            self.source_language = data.get('source_language', None)
            self.target_language = data.get('target_language', None)
            categories = data.get('categories', [])
            phenomena = data.get('phenomena', [])
            how_many = data.get('howMany', None)
            percentage = data.get('percentage', None)
            

            queryset = TestItem.objects.all()

            langpair_query = Langpair.objects.all()
            
            if self.source_language:
                langpair_query = langpair_query.filter(source_language__code=self.source_language)
            if self.target_language:
                langpair_query = langpair_query.filter(target_language__code=self.target_language)
            
            testset_query = Testset.objects.filter(langpair__in=langpair_query)
            
        
            queryset = TestItem.objects.filter(testset__in=testset_query)
        
            if categories:
               queryset = queryset.filter(phenomenon__category__name__in=categories)
               
            
            if phenomena:
                queryset = queryset.filter(phenomenon__name__in=phenomena)
            
            if percentage:
                total_count = queryset.count()
                how_many = (total_count * int(percentage)) // 100
                
            if how_many is not None:
                how_many = int(how_many)  

            # Serialize the results
            self.filtered_items = queryset[:how_many]  
            request.session['filtered_items'] = [item.id for item in self.filtered_items]
            request.session.modified = True
            request.session.save()
            print(f"Session ID in filter_test_items: {request.session.session_key}")

            serializer = FilteredTestItemSerializer(self.filtered_items, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['post'])
    def download_text_file(self, request):
        
        try:
            data = request.data
            scrambling_factor = int(data.get('scramblingFactor', 1)) 
            testitem_ids = data.get('content', []) 

            test_items = list(TestItem.objects.filter(id__in=testitem_ids))
        
            if len(test_items) < scrambling_factor:
                return Response({'error': 'Not enough items for the given scrambling_factor.'}, status=status.HTTP_400_BAD_REQUEST)

            rand_list = random.sample(range(1, len(test_items) * scrambling_factor + 1), len(test_items))
        
            langpair_query = Langpair.objects.all()
            if self.source_language:
                langpair_query = langpair_query.filter(source_language__code=self.source_language)
            if self.target_language:
                langpair_query = langpair_query.filter(target_language__code=self.target_language)
            
            testset = Testset.objects.filter(langpair__in=langpair_query).first() 
            new_template = Template.objects.create(
                select=0.0,
                scramble_factor=scrambling_factor,
                testset=testset
            )
           
            self.create_template_positions(test_items, rand_list, new_template)
    
            # Generate the text file content
            text_file_content = self.generate_text_file_content(new_template)
            
            # Return the file as a downloadable response
            return Response({
                'template_id': new_template.id,  # Include the template ID
                'text_file_content': text_file_content  # Include the text file content
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error in download_text_file: {str(e)}")  # Log the error
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    def create_template_positions(self, filtered_items, rand_list, template):
        try:
            with transaction.atomic():
                for i, test_item in enumerate(filtered_items):
                    position = rand_list[i]
                    
                    TemplatePosition.objects.create(
                        template=template,
                        test_item=test_item,
                        pos=position
                    )
          
        except Exception as e:
            print(f"Error creating template positions: {str(e)}")
            
    def generate_text_file_content(self ,template):
           
            try:
                template_positions = TemplatePosition.objects.filter(template=template)
                print("Template Positions" , template_positions)
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

            except Exception as e:
                print("error", e)
            
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
    
    def check_rules_for_translation(self, translation):
        rules = Rule.objects.filter(item=translation.test_item)
      
        positive_regex_rules = [rule for rule in rules if rule.regex and rule.positive]
        negative_regex_rules = [rule for rule in rules if rule.regex and not rule.positive]
        positive_token_rules = [rule for rule in rules if not rule.regex and rule.positive]
        negative_token_rules = [rule for rule in rules if not rule.regex and not rule.positive]

        positive_regex_match = any(re.search(rule.string, translation.sentence) for rule in positive_regex_rules)
        negative_regex_match = any(re.search(rule.string, translation.sentence) for rule in negative_regex_rules)
        positive_token_match = any(re.search(rule.string, translation.sentence) for rule in positive_token_rules)
        negative_token_match = any(re.search(rule.string, translation.sentence) for rule in negative_token_rules)

        if (positive_regex_match and negative_regex_match) or (positive_token_match and negative_token_match):
            translation.label = Translation.Label.CONFLICT
        elif positive_regex_match:
            translation.label = Translation.Label.PASS
        elif negative_regex_match:
            translation.label = Translation.Label.FAIL
        elif positive_token_match:
            translation.label = Translation.Label.PASS
        elif negative_token_match:
            translation.label = Translation.Label.FAIL
        else:
            translation.label = Translation.Label.WARNING

        translation.save()
    
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
                        
                        self.check_rules_for_translation(translation)

            return Response({'message': 'Reports and Translation Objects have been created'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            raise ValidationError({'error': str(e)})
        
class TranslationViewSet(viewsets.ModelViewSet):
    queryset = Translation.objects.all()
    serializer_class = TranslationSerializer
    
class ReportTranslationsListView(ListAPIView):
    serializer_class = TranslationSerializer

    def get_queryset(self):
        # Get the report ID from the URL parameters
        report_id = self.kwargs['report_id']

        # Filter translations by the specified report ID
        queryset = Translation.objects.filter(report_id=report_id)
        return queryset
    
class RulesByTranslationId(APIView):
    def get(self, request, translation_id):
        translation = get_object_or_404(Translation, pk=translation_id)
        test_item = translation.test_item
        rules = Rule.objects.filter(item=test_item)
        rules_data = RuleSerializer(rules, many=True).data  
        response_data = {
            'rules': rules_data,
            'source_sentence': test_item.source_sentence,
            'target_sentence': translation.sentence,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
logger = logging.getLogger(__name__)

class UpdateRulesView(APIView):
    def post(self, request):
        data = request.data
        label = data.get('label')
        translation_id = data.get('translation_id')
        positive_regexes = data.get('positive_regexes', [])
        negative_regexes = data.get('negative_regexes', [])
        positive_tokens = data.get('positive_tokens', [])
        negative_tokens = data.get('negative_tokens', [])

        # Get the Translation and associated TestItem
        translation = get_object_or_404(Translation, pk=translation_id)
         # Update the label of the translation based on the provided label
        if label == "PASS":
            translation.label = 1
        elif label == "FAIL":
            translation.label = 2
        elif label == "CONFLICT":
            translation.label = 4
        else:
            translation.label = 3
        translation.save()
        logger.info(f"Updated translation label: {translation.label}")
        
        test_item = translation.test_item
        # Collect all existing rule IDs from the request data
        existing_rule_ids = set()

        # Process positive regexes
        for regex in positive_regexes:
            if 'id' in regex and regex['id']:  # Update existing rule
                rule = get_object_or_404(Rule, pk=regex['id'], item=test_item)
                rule.string = regex['string']
                rule.save()
                existing_rule_ids.add(rule.id)
                logger.info(f"Updated rule: {rule.id}")
            else:  # Create new rule
                new_rule = Rule.objects.create(item=test_item, string=regex['string'], regex=True, positive=True)
                existing_rule_ids.add(new_rule.id)
                logger.info(f"Created new rule: {new_rule.id}")

        # Process negative regexes
        for regex in negative_regexes:
            if 'id' in regex and regex['id']:  # Update existing rule
                rule = get_object_or_404(Rule, pk=regex['id'], item=test_item)
                rule.string = regex['string']
                rule.save()
                existing_rule_ids.add(rule.id)
                logger.info(f"Updated rule: {rule.id}")
            else:  # Create new rule
                new_rule = Rule.objects.create(item=test_item, string=regex['string'], regex=True, positive=False)
                existing_rule_ids.add(new_rule.id)
                logger.info(f"Created new rule: {new_rule.id}")

        # Process positive tokens
        for token in positive_tokens:
            if 'id' in token and token['id']:  # Update existing rule
                rule = get_object_or_404(Rule, pk=token['id'], item=test_item)
                rule.string = token['string']
                rule.save()
                existing_rule_ids.add(rule.id)
                logger.info(f"Updated rule: {rule.id}")
            else:  # Create new rule
                new_rule = Rule.objects.create(item=test_item, string=token['string'], regex=False, positive=True)
                existing_rule_ids.add(new_rule.id)
                logger.info(f"Created new rule: {new_rule.id}")

        # Process negative tokens
        for token in negative_tokens:
            if 'id' in token and token['id']:  # Update existing rule
                rule = get_object_or_404(Rule, pk=token['id'], item=test_item)
                rule.string = token['string']
                rule.save()
                existing_rule_ids.add(rule.id)
                logger.info(f"Updated rule: {rule.id}")
            else:  # Create new rule
                new_rule = Rule.objects.create(item=test_item, string=token['string'], regex=False, positive=False)
                existing_rule_ids.add(new_rule.id)
                logger.info(f"Created new rule: {new_rule.id}")

        # Delete removed rules
        deleted_rules = Rule.objects.filter(item=test_item).exclude(id__in=existing_rule_ids)
        deleted_count, _ = deleted_rules.delete()
        logger.info(f"Deleted {deleted_count} rules")

        # Log the current rules in the database for debugging
        current_rules = Rule.objects.filter(item=test_item)
        logger.info(f"Current rules in the database: {RuleSerializer(current_rules, many=True).data}")

        # Ensure source and translation text are included in the response
        response_data = {
            'source_sentence': test_item.source_sentence,
            'target_sentence': translation.sentence,
            'created_rules': RuleSerializer(Rule.objects.filter(id__in=existing_rule_ids, item=test_item), many=True).data,
            
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
class TemplateWithReportViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateWithReportSerializer

class CompareReportsView(APIView):
    def post(self, request):
        report_ids = request.data.get('report_ids', [])
        categories = Category.objects.all()
        result = {}
        all_accuracies = {}
        
        report_pass_counts = {report_id: 0 for report_id in report_ids}
        report_testitems = {report_id: 0 for report_id in report_ids}
        
        translations_prefetch = Prefetch(
            'translation_set',
            queryset=Translation.objects.filter( #fetch translation objects that match following condits:
                report__id__in=report_ids, #translation belong to report_id and has a pass or fail label
                label__in=[Translation.Label.PASS, Translation.Label.FAIL]
            ).order_by('report_id'),
            to_attr='filtered_translations'
        )
        for category in categories:
            test_items = TestItem.objects.filter(
                phenomenon__category=category,
                translation__report__id__in=report_ids,
                translation__label__in=[Translation.Label.PASS, Translation.Label.FAIL]
            ).prefetch_related(translations_prefetch).distinct()

            comparison_array = []
            for test_item in test_items:
                translations = test_item.filtered_translations
                present_report_ids = {t.report_id for t in translations}
                
                
                if all(rid in present_report_ids for rid in report_ids):
                    # Sort translations by report_ids order
                    translations_sorted = sorted(
                        translations, 
                        key=lambda t: report_ids.index(t.report_id)
                    )
                    row = []
                    for t in translations_sorted:
                        if t.label == Translation.Label.PASS:
                            row.append(1)
                            report_pass_counts[t.report_id] += 1
                        else:
                            row.append(0)
                        report_testitems[t.report_id] += 1
                    comparison_array.append(row)
                    
            accuracies, category_average = self.calculate_accuracies(comparison_array,report_ids)
            n_test_items = len(comparison_array)
            
            all_accuracies[category.name] =  {
                'accuracies': accuracies,
                'n_test_items': n_test_items
            }
            accuracy_df = pd.DataFrame(
                [accuracies],
                index=[category.name],
                columns=report_ids
            )
            accuracy_df['n_test_items'] = n_test_items
            
            styled = accuracy_df.apply(
                lambda row: self.annotate_significance(row), 
                axis=1
            ).iloc[0]
            
           
            result[category.name] = {
                "average": category_average,
                "data": [
                    {
                        "accuracy": accuracy,
                        "significant": styled
                    }
                    for accuracy, styled in zip(accuracies, styled)
                ]
            }
        
        micro_averages = {}
        macro_averages = {} 

        for report_id in report_ids:
            total_category_averages = sum([cat_data['average'] for cat_data in result.values()])
            micro_averages[report_id] = (total_category_averages / len(categories))
            
            if report_testitems[report_id] > 0:
                macro_averages[report_id] = ((report_pass_counts[report_id] / report_testitems[report_id]) * 100)
            else:
                macro_averages[report_id] = 0.00

        return Response({
            "result": result,
            "micro_averages": micro_averages,
            "macro_averages": macro_averages,
            
        })
    
    def calculate_accuracies(self, comparison_array, report_ids):  
        if comparison_array:
            accuracies = [
                sum(col) / len(comparison_array) if len(comparison_array) > 0 else 0
                for col in zip(*comparison_array)
            ]
            category_average = (sum(accuracies) / len(accuracies)) if accuracies else 0.00
        else:
            accuracies = [0] * len(report_ids) 
            category_average = 0.00
        return accuracies, category_average 
        
    def annotate_significance(self, row, alpha= 0.05, significant=True, non_significant=False):
        best_accuracy = row.max()
        n = len(row)
        comparison_results = []
        
        for i, accuracy in enumerate(row):
            if accuracy == best_accuracy:
                comparison_results.append(non_significant) 
                continue # Bold the best system
            else:
                if n > 1:
                    std_dev = np.sqrt((accuracy * (1 - accuracy)) / n)
                    if std_dev > 0:
                        z_score = (best_accuracy - accuracy) / std_dev
                        critical_z_value = norm.ppf(1 - alpha)  # One-tailed Z-test for α = 0.05
                        
                        if z_score < critical_z_value:
                            comparison_results.append(significant)  
                        else:
                            comparison_results.append(non_significant) 
                    else:
                        comparison_results.append(significant) 
                else:
                    comparison_results.append(non_significant)  
        return comparison_results
    
class MatchingReportsView(APIView): 
    def get(self,request, template_id): 
        try: 
            template = Template.objects.get(id=template_id)  
            engine_names = template.report_set.values_list('engine', flat=True).distinct() 
            langpair = template.testset.langpair 
            matching_reports = Report.objects.filter(engine__in=engine_names, template__testset__langpair=langpair).exclude(template = template) 
            serializer = ReportSerializer(matching_reports, many=True) 
            return Response(serializer.data, status=status.HTTP_200_OK) 
        except Template.DoesNotExist: 
            return Response({"error": "Template not found."}, status=status.HTTP_404_NOT_FOUND)

class CategoryTestItemsView(APIView):
    def get(self, request, category):
        try:
            category_obj = get_object_or_404(Category, name=category)

            report_ids = request.GET.getlist("reports")

            if len(report_ids) == 1 and ',' in report_ids[0]:
                report_ids = report_ids[0].split(',')
           

            # Convert report_ids to integers
            report_ids = [int(report_id) for report_id in report_ids]
          
            test_items = TestItem.objects.filter(phenomenon__category=category_obj)

            # Serialize the test items with translations
            serializer = TestItemWithTranslationsSerializer(test_items, many=True, context={'report_ids': report_ids})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateTranslationLabelView(APIView):
    def post(self, request):
        translationid = request.data.get("translation_id")
        label = request.data.get("label")
        
        label_mapping = {
            "PASS": 1,
            "FAIL": 2,
            "WARNING": 3,
            "CONFLICT": 4
        }
        new_label = label_mapping.get(label)
        translation = get_object_or_404(Translation, pk=translationid)
        
        if new_label is not None:
            translation.label = new_label
            translation.save()
            return Response({'message': 'Label updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid label'}, status=status.HTTP_400_BAD_REQUEST)
    