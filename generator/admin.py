from django.contrib import admin

# Register your models here.
from evaluator.models import TestItem
from evaluator.models import Testset
from evaluator.models import Phenomenon
from evaluator.models import Langpair
from evaluator.models import Language
from evaluator.models import Category
from evaluator.models import Distractor
from evaluator.models import Template
from evaluator.models import Rule
from evaluator.models import Report
from evaluator.models import TemplatePosition
from evaluator.models import Translation



admin.site.register(TestItem)
admin.site.register(Testset)
admin.site.register(Phenomenon)
admin.site.register(Langpair)
admin.site.register(Language)
admin.site.register(Category)
admin.site.register(Distractor)
admin.site.register(Template)
admin.site.register(Rule)
admin.site.register(Report)
admin.site.register(TemplatePosition)
admin.site.register(Translation)