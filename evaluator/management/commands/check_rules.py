from django.core.management.base import BaseCommand
from evaluator.models import Translation, Rule
from evaluator.serializers import RuleSerializer

class Command(BaseCommand):
    help = 'Check if rules are created correctly for a given translation or test item'

    def add_arguments(self, parser):
        parser.add_argument('translation_id', type=int, help='ID of the Translation to check')

    def handle(self, *args, **kwargs):
        translation_id = kwargs['translation_id']
        try:
            translation = Translation.objects.get(pk=translation_id)
            test_item = translation.test_item
            rules = Rule.objects.filter(item=test_item)

            if rules.exists():
                self.stdout.write(self.style.SUCCESS(f'Found {rules.count()} rules for TestItem with ID {test_item.id}:'))
                for rule in rules:
                    self.stdout.write(self.style.SUCCESS(
                        f"ID: {rule.id}, String: {rule.string}, Regex: {rule.regex}, Positive: {rule.positive}"
                    ))
            else:
                self.stdout.write(self.style.WARNING(f'No rules found for TestItem with ID {test_item.id}'))

        except Translation.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Translation with ID {translation_id} does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
