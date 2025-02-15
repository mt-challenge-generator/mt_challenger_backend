from django.utils import timezone
import re
from django.core.management.base import BaseCommand
from django.db import connections
from evaluator.models import Language, Langpair, Category, Phenomenon, Distractor, Testset, Template, TemplatePosition, TestItem, Rule, Report, Translation

class Command(BaseCommand):
    help = 'Import data from the old MySQL database to the new Django SQLite database'

    def migrate_languages(self):
        """Migrate languages from the old database"""
        with connections['old_mysql'].cursor() as cursor:
            cursor.execute("SELECT DISTINCT direction FROM rules Limit 50")
            rules_languages = cursor.fetchall()

            # Extract source and target language codes from the 4-letter codes
            unique_language_codes = set()
            for code_tuple in rules_languages:
                code = code_tuple[0]
                if len(code) == 4:  # Ensure the code is exactly 4 characters
                    source_lang = code[:2]
                    target_lang = code[2:]
                    unique_language_codes.add(source_lang)
                    unique_language_codes.add(target_lang)

            # Filter out existing languages
            existing_codes = set(Language.objects.values_list('code', flat=True))
            new_language_codes = unique_language_codes - existing_codes

            # Create Language objects for new codes
            language_objects = [
                Language(code=lang_code, name=f"Language {lang_code}")
                for lang_code in new_language_codes
            ]

            if language_objects:
                Language.objects.bulk_create(language_objects)
                print(f'Migrated {len(language_objects)} new languages.')
            else:
                print("No new languages to migrate.")
                
    def migrate_langpairs_testset(self):
        with connections['old_mysql'].cursor() as cursor:
            cursor.execute("SELECT DISTINCT direction FROM reports")
            directions = cursor.fetchall()
            langpair_objects = []
            for direction in directions:
                source, target = direction[0][:2], direction[0][2:]
                source_lang = Language.objects.get(code=source)
                target_lang = Language.objects.get(code=target)
                langpair_objects.append(Langpair(source_language=source_lang, target_language=target_lang))
            Langpair.objects.bulk_create(langpair_objects) 
            self.stdout.write(f"Migrated {len(langpair_objects)} langpairs.")
            testsets = []
            for langpair in langpair_objects:
                testsets.append({
                    'langpair': langpair,
                    'description': f'Test set for {langpair.source_language} to {langpair.target_language.code}',
                })
            Testset.objects.bulk_create([
            Testset(langpair=testset['langpair'], description=testset['description'])
            for testset in testsets
        ])
        self.stdout.write(f'Migrated {len(testsets)} testsets.')
            
    def migrate_categories_and_phenomena(self):
        with connections['old_mysql'].cursor() as cursor:
            cursor.execute("SELECT DISTINCT category, barrier FROM rules")
            rules_data = cursor.fetchall()
            categories = {category for category, _ in rules_data}
            category_objects = [Category(name=cat) for cat in categories]
            Category.objects.bulk_create(category_objects) 
            
            category_map = {cat.name: cat for cat in Category.objects.all()}
            phenomena = [
            Phenomenon(name=barrier, category=category_map[category])
                    for category, barrier in rules_data]
            Phenomenon.objects.bulk_create(phenomena)
            self.stdout.write(f"Migrated {len(categories)} categories and {len(phenomena)} phenomena.")

    def migrate_distractors(self):
        """Migrate distractors from the old database"""
        with connections['old_mysql'].cursor() as cursor:
            cursor.execute("SELECT text, lang FROM distractors Limit 50")
            distractors = cursor.fetchall()
            distractor_objects = []
            for text, lang_code in distractors:
                language = Language.objects.get(code=lang_code)
                distractor_objects.append(Distractor(text=text, language=language))
            Distractor.objects.bulk_create(distractor_objects)
            self.stdout.write(self.style.SUCCESS(f'Migrated {len(distractor_objects)} distractors.'))
    
    def migrate_testitems_and_rules(self):
        with connections['old_mysql'].cursor() as cursor:
            cursor.execute(
                "SELECT id, testPoint, version, barrier, source, comment, direction, positiveTokens, positiveRegex, negativeTokens, negativeRegex FROM rules"
            )
            rules_data = cursor.fetchall()

            
            phenomena_map = {phen.name: phen for phen in Phenomenon.objects.all()}
            test_items = []
            rule_objects = []

            for rule_id, test_point, version, barrier, source, comment, direction, positiveTokens, positiveRegex, negativeTokens, negativeRegex in rules_data:
                # Handle NULL or empty testPoint by assigning a default value (e.g., 0)
                if not test_point:  # Handles NULL or ""
                    test_point = 0  # Default value
                else:
                    try:
                        test_point = int(test_point)  # Convert to integer
                    except ValueError:
                        self.stderr.write(f"Invalid testPoint '{test_point}' for rule ID {rule_id}. Skipping.")
                        continue
                
                # Handle NULL or empty version by assigning a default value (e.g., 0) or None
                if not version:  # Handles NULL or empty string
                    version = None  # Set to None if the field allows NULL
                else:
                    try:
                        version = int(version)  
                    except ValueError:
                        self.stderr.write(f"Invalid version '{version}' for rule ID {rule_id}. Skipping.")
                        continue
                
                phenomenon = phenomena_map.get(barrier)
                source_code = direction[:2]
                target_code = direction[2:]

                # Fetch the Langpair
                try:
                    langpair = Langpair.objects.get(
                        source_language__code=source_code,
                        target_language__code=target_code
                    )
                except Langpair.DoesNotExist:
                    self.stderr.write(f"No Langpair found for {source_code} -> {target_code}. Skipping rule ID {rule_id}.")
                    continue

                # Fetch the Testset
                testset = Testset.objects.filter(langpair=langpair).first()
                if phenomenon:
                    test_item = TestItem(
                        legacy_id=rule_id,
                        legacy_testpoint=test_point,
                        legacy_version=version,
                        phenomenon=phenomenon,
                        source_sentence=source,
                        testset=testset,
                        created_time=timezone.now(),
                        comment=comment
                    )
                    test_items.append(test_item)

                    # Add rules
                    if positiveRegex:
                        rule_objects.append(Rule(
                            item=test_item,
                            string=positiveRegex,
                            regex=True,
                            positive=True
                        ))
                    if positiveTokens:
                        rule_objects.append(Rule(
                            item=test_item,
                            string=positiveTokens,
                            regex=False,
                            positive=True
                        ))
                    if negativeTokens:
                        rule_objects.append(Rule(
                            item=test_item,
                            string=negativeTokens,
                            regex=False,
                            positive=False
                        ))
                    if negativeRegex:
                        rule_objects.append(Rule(
                            item=test_item,
                            string=negativeRegex,
                            regex=True,
                            positive=False
                        ))

            # Bulk insert for performance
            TestItem.objects.bulk_create(test_items)
            Rule.objects.bulk_create(rule_objects)

            self.stdout.write(f'Migrated {len(test_items)} test items and {len(rule_objects)} rules.')

    def migrate_templates_and_positions(self):
        with connections['old_mysql'].cursor() as cursor:
            # Step 1: Fetch data from template_meta
            cursor.execute("SELECT id, meta FROM template_meta")
            template_meta_data = cursor.fetchall()

            templates = []
            template_positions = []

            for meta_id, meta in template_meta_data:
                try:
                  
                    select, scramble_factor, categories_and_phenomena = self.parse_meta_string(meta) 

                    categories = Category.objects.filter(name__in=categories_and_phenomena)
                    phenomena = Phenomenon.objects.filter(name__in=categories_and_phenomena)

                    cursor.execute("SELECT id, sentence, pos, lang FROM templates WHERE id = %s", [meta_id])
                    templates_data = cursor.fetchall()  
              
                    lang = templates_data[0][3]
                    source_code = lang[:2]
                    target_code = lang[2:]
                    source_lang = Language.objects.get(code=source_code)
                    target_lang = Language.objects.get(code=target_code)

                        # Get the Testset associated with the Langpair
                    langpair = Langpair.objects.get(source_language=source_lang, target_language=target_lang)
                    testset = Testset.objects.get(langpair=langpair)

                    template = Template(
                            legacy_id=meta_id, #I only have 90 templates form previous database starting from 313 to 402
                            testset=testset,
                            name=f"Template {meta_id}",
                            select=select,
                            scramble_factor=scramble_factor,
                            created_time = timezone.now() #not working
                        )
                    template.save()  # Save ManyToMany relationships
                    template.categories.set(categories)
                    template.phenomena.set(phenomena)
                    
                    for _ , sentence, pos, _ in templates_data:
                        try:
                            testitem = TestItem.objects.get(legacy_id=sentence, testset=testset) 
                        except TestItem.DoesNotExist:
                            print(f"TestItem in template_meta Id { meta_id } with legacy_id {sentence} not found.")
                            continue
                        
                        template_position = TemplatePosition(
                            template=template,
                            test_item=testitem, 
                            pos=pos,
                        )
                        template_positions.append(template_position)
                except Exception as e:
                    print(f"Error processing template_meta ID {meta_id}: {e}")

            if template_positions:
                TemplatePosition.objects.bulk_create(template_positions)

        print(f"Migrated {len(templates)} templates and {len(template_positions)} template positions.")

    def parse_meta_string(self, meta):
        select_match = re.search(r"select (\d+\.\d+)", meta)
        scramble_factor_match = re.search(r"scramble factor:(\d+\.\d+)", meta)
        categories_and_phenomena = re.findall(r"from (.+?)\[", meta)

        select = float(select_match.group(1)) if select_match else 0.0
        scramble_factor = float(scramble_factor_match.group(1)) if scramble_factor_match else 0.0
        categories_and_phenomena = categories_and_phenomena[0].split(",") if categories_and_phenomena else []

        return select, scramble_factor, categories_and_phenomena
    
    def migrate_reports(self):
        with connections['old_mysql'].cursor() as cursor:
            cursor.execute("SELECT id, templateid, client, type, comment, time FROM reports")
            reports_data = cursor.fetchall()

            reports = []

            for report_data in reports_data:
                try:
                    report_id, template_id, engine, engine_type, comment, time = report_data
                    
                    # Ensure the template exists
                    try:
                        template = Template.objects.get(legacy_id=template_id) #I can only get templates from legacy_id 313 to 402
                    except Template.DoesNotExist:
                        self.stderr.write(f"Template with legacy_id {template_id} not found. Skipping report ID {report_id}.")
                        continue

                    report = Report(
                        legacy_id=report_id,
                        template=template,
                        engine=engine,
                        engine_type=engine_type,
                        comment=comment,
                        created_time=time,
                    )
                    report.save()
                    reports.append(report)

                except Exception as e:
                    self.stderr.write(f"Error processing report with legacy_id {report_id}: {e}")

            self.stdout.write(f"Migrated {len(reports)} reports.")
            
    def migrate_translations(self):
        with connections['old_mysql'].cursor() as cursor:
            cursor.execute("SELECT reportid, sentenceid, translation, pass FROM sentences ")
            sentences_data = cursor.fetchall()

            translations = []

            for reportid, sentenceid, translation, label_value in sentences_data:
                try:
                    report = Report.objects.get(legacy_id=reportid)

                    # Retrieve all TestItems with the given legacy_id
                    test_items = TestItem.objects.filter(legacy_id=sentenceid, testset = report.template.testset  )
                    

                    # Create a Translation for each TestItem
                    for test_item in test_items:
                        label = label_value if label_value in [1, 2, 3, 4] else 3

                        translation_obj = Translation(
                            legacy_id=sentenceid,
                            test_item=test_item,
                            report=report,
                            sentence=translation,
                            label=label,
                        )
                        translations.append(translation_obj)

                except Exception as e:
                    self.stderr.write(f"Error processing sentence ID {sentenceid}: {e}")

            Translation.objects.bulk_create(translations)
            self.stdout.write(f"Migrated {len(translations)} translations.")
    
    def handle(self, *args, **kwargs):
        self.migrate_languages() 
        self.migrate_langpairs_testset()
        self.migrate_categories_and_phenomena()
        self.migrate_distractors()
        self.migrate_testitems_and_rules()
        self.migrate_templates_and_positions()
        self.migrate_reports()
        self.migrate_translations()   
