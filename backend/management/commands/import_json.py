from datetime import datetime

from django.core.management import BaseCommand
import json

from backend.models import TestItem, Category, Phenomenon, Language, Langpair, Testset


class Command(BaseCommand):
    help = 'Imports legacy test suite data from given JSON file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='filename of the JSON file to be imported')

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        with open(filename) as f:
            json_object = json.load(f)
            for incoming in json_object['items']:
                item = TestItem()

                incoming_langpair = incoming['langpair']
                source_language_code = incoming_langpair[:2]
                target_language_code = incoming_langpair[2:]

                source_language, _ = Language.objects.get_or_create(code=source_language_code)
                target_language, _ = Language.objects.get_or_create(code=target_language_code)

                langpair, _ = Langpair.objects.get_or_create(
                    source_language=source_language,
                    target_language=target_language
                )

                category, _ = Category.objects.get_or_create(
                    name=incoming['category'],
                    langpair=langpair
                )

                phenomenon, _ = Phenomenon.objects.get_or_create(
                    name=incoming['phenomenon'],
                    category=category)

                testset, _ = Testset.objects.get_or_create(name="Legacy")

                testitem = TestItem()
                testitem.phenomenon = phenomenon
                testitem.source_sentence = incoming['source_sentence']
                testitem.id = incoming['id']
                testitem.testset = testset
                testitem.generation_time = datetime.now()

                # TODO: positive and regular expressions are not imported
                testitem.save()


