import os
import json
import codecs
from django.core.management.base import BaseCommand
from evaluator.models import Testset, TestItem, Phenomenon, Language, Langpair, Category

class Command(BaseCommand):
    help = 'Import data from JSON file'

    def handle(self, *args, **kwargs):
        # Set up Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mt_challenger_backend.settings')
        import django
        django.setup()

        # Path to the JSON file (assuming it's in the evaluator directory)
        json_file_name = 'testsuite_en-de.json'
        json_file_path = self.find_json_file(json_file_name)

        if not json_file_path:
            print(f"JSON file '{json_file_name}' not found.")
            return

        # Load JSON data
        with codecs.open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Iterate over the items in the JSON data
        for item in data['items'][:50]:
            # Assuming 'langpair' is a dictionary with 'source_language' and 'target_language' keys
            langpair = item['langpair']
            source_language_code = langpair[:2]
            target_language_code = langpair[-2:]
            
                # Set the language names based on language codes
            source_language_name = "English" if source_language_code == "en" else "Unknown"
            target_language_name = "English" if source_language_code == "en" else "Unknown"
            
            source_language_name = "German" if source_language_code == "de" else "Unknown"
            target_language_name = "German" if target_language_code == "de" else "Unknown"

            
            source_language_name = "Russain" if source_language_code == "rn" else "Unknown"
            target_language_name = "Russain" if target_language_code == "rn" else "Unknown"
            
            # Create or get Language objects with their names
            source_language, _ = Language.objects.get_or_create(code=source_language_code, defaults={'name': source_language_name})
            target_language, _ = Language.objects.get_or_create(code=target_language_code, defaults={'name': target_language_name})


            langpair, _ = Langpair.objects.get_or_create(
                source_language=source_language,
                target_language=target_language
            )

            # Check if a Testset with the current Langpair exists
            testset, created = Testset.objects.get_or_create(
                name=f"{source_language_code}-{target_language_code}",  # Adjust as per your naming convention
                langpair=langpair
            )

            if created:
                # Populate testset description if needed
                testset.description = f"Testset for {source_language_code}-{target_language_code}"
                testset.save()

            category, _ = Category.objects.get_or_create(name=item['category'])

            phenomenon, _ = Phenomenon.objects.get_or_create(
                category=category,
                name=item['phenomenon']
            )

            TestItem.objects.create(
                legacy_id=item['id'],
                testset=testset,
                phenomenon=phenomenon,
                source_sentence=item['source_sentence'],
                comment=" This is a comment"
            )

    def find_json_file(self, file_name):
        """
        Find JSON file by recursively searching parent directories
        """
        current_dir = os.path.abspath(__file__)  # Get absolute path of current file
        while True:
            # Check if file exists in current directory
            file_path = os.path.join(current_dir, file_name)
            if os.path.exists(file_path):
                return file_path

            # Move up one directory
            parent_dir = os.path.dirname(current_dir)
            # Break loop if reached root directory
            if parent_dir == current_dir:
                break
            current_dir = parent_dir

        # File not found
        return None
