from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=30)


class Langpair(models.Model):
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_language')
    target_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='target_language')


class Testset(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=250)


class Category(models.Model):  # values from rules.category
    name = models.CharField(max_length=30)
    langpair = models.ForeignKey(Langpair, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Categories"


class Phenomenon(models.Model):  # values from rules.barrier
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Phenomena"


class TestItem(models.Model):  # former rules
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.CharField(max_length=10)  # former rules.ID
    legacy_testpoint = models.SmallIntegerField()  # former rules.testPoint
    legacy_version = models.SmallIntegerField()  # former rules.version
    testset = models.ForeignKey(Testset, on_delete=models.CASCADE)
    phenomenon = models.ForeignKey(Phenomenon, on_delete=models.CASCADE)  # resolve from rules.barrier
    source_sentence = models.CharField(max_length=500)  # former rules.source
    comment = models.CharField(max_length=100)  # former rules.comment
    created_time = models.DateTimeField(auto_now_add=True)


class Rule(models.Model):
    item = models.ForeignKey(TestItem, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class PositiveRule(Rule):  # former rules.positiveRegex
    regex = models.CharField(max_length=200)


class NegativeRule(models.Model):  # former rules.negativeRegex
    regex = models.CharField(max_length=200)


class PositiveToken(models.Model):  # former rules.positivetokens
    sentence = models.CharField(max_length=200)


class NegativeToken(models.Model):  # former rules.negativetokens
    sentence = models.CharField(max_length=200)


class Translation(models.Model):  # former sentences
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.CharField(max_length=10, blank=True)  # former sentences.sentenceid

    class Label(models.IntegerChoices):
        PASS = 1
        FAIL = 2
        WARNING = 3

    test_item = models.ForeignKey(TestItem, on_delete=models.CASCADE)
    sentence = models.CharField(max_length=500)  # former sentences.translation
    label = models.IntegerField(choices=Label.choices, default=3)  # former sentences.pass


class Template(models.Model):  # former template_meta
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.SmallIntegerField(blank=True, null=True)  # former template_meta.id
    description = models.CharField(max_length=50, blank=True)
    select = models.DecimalField(decimal_places=2)  # former template_meta.met.select=
    testset = models.ForeignKey(Testset, on_delete=models.CASCADE)
    phenomena = models.ManyToManyField(Phenomenon)  # resolve from template_meta.from
    scramble_factor = models.DecimalField(decimal_places=1)  # former template_meta.meta.scramble_factor
    created_time = models.DateTimeField(auto_now_add=True)


class Report(models.Model):  # former reports
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.SmallIntegerField(blank=True, null=True)  # former reports.id
    template = models.ForeignKey(Template, on_delete=models.CASCADE)  # resolve from reports.templateid
    client = models.CharField(max_length=50)  # former reports.client
    comment = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)  # former reports.time


class TemplatePositions(models.Model):  # former templates
    template = models.ForeignKey(Template, on_delete=models.CASCADE)  # resolve from templates.id
    test_item = models.ForeignKey(TestItem, on_delete=models.CASCADE)  # resolve from templates.sentences
    pos = models.IntegerField()  # former templates.pos


class Distractor(models.Model):  # former distractors
    text = models.CharField(max_length=500)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

