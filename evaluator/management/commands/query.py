from evaluator.models import Language, Langpair, Category, Phenomenon, Distractor, Testset, Template, TemplatePosition, TestItem, Rule, Report, Translation

from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = 'Import data from the old MySQL database to the new Django SQLite database'
    def fetch_languages(self):
        languages = Language.objects.all()
        for language in languages:
            print(f"Code: {language.code}, Name: {language.name}")

    def fetch_testsets(self):
        testsets = Testset.objects.all()
        for testset in testsets:
            print(f"Name: {testset.name}, Description: {testset.description}")
            
    def fetch_testitems(self):
        testitems= TestItem.objects.filter(legacy_id = "00385001" )
        for testitem in testitems:
            print(f"lagacy Id :{testitem.legacy_id} and source sentence {testitem.source_sentence}")
    def fetch_templates(self):
        templates = Template.objects.filter(legacy_id="294")
        for template in templates:
            print(f"Templates:{template.id}",)
            
    def handle(self, *args, **kwargs):
        #print("Fetching Languages:")
        #self.fetch_languages()
        
        #print("\nFetching Testsets:")
        #self.fetch_testsets()
        
        #self.fetch_testitems()
        
        self.fetch_templates()
