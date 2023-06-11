from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=30)


class Langpair(models.Model):
    source_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="source_language"
    )
    target_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="target_language"
    )


class Testset(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=250)
    langpair = models.ForeignKey(Langpair, on_delete=models.CASCADE)


class Category(models.Model):  # values from rules.category
    name = models.CharField(max_length=30)

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
    phenomenon = models.ForeignKey(
        Phenomenon, on_delete=models.CASCADE
    )  # resolve from rules.barrier
    source_sentence = models.CharField(max_length=500)  # former rules.source
    comment = models.CharField(max_length=100)  # former rules.comment
    created_time = models.DateTimeField(auto_now_add=True)


class Rule(models.Model):
    item = models.ForeignKey(TestItem, on_delete=models.CASCADE)
    string = models.CharField(max_length=200)
    regex = models.BooleanField(default=True)
    positive = models.BooleanField(default=True)


class Template(models.Model):  # former template_meta
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.SmallIntegerField(
        blank=True, null=True
    )  # former template_meta.id
    name = models.CharField(max_length=50, blank=True)
    select = models.DecimalField(
        max_digits=10, decimal_places=2
    )  # former template_meta.met.select=
    testset = models.ForeignKey(Testset, on_delete=models.CASCADE)
    phenomena = models.ManyToManyField(Phenomenon)  # resolve from template_meta.from
    categories = models.ManyToManyField(Category)  # resolve from template_meta.from
    scramble_factor = models.DecimalField(
        max_digits=5, decimal_places=1
    )  # former template_meta.meta.scramble_factor
    created_time = models.DateTimeField(auto_now_add=True)


class Report(models.Model):  # former reports
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.SmallIntegerField(blank=True, null=True)  # former reports.id
    template = models.ForeignKey(
        Template, on_delete=models.CASCADE
    )  # resolve from reports.templateid
    engine = models.CharField(max_length=50)  # former reports.client
    comment = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)  # former reports.time


class Translation(models.Model):  # former sentences
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.CharField(
        max_length=10, blank=True
    )  # former sentences.sentenceid

    class Label(models.IntegerChoices):
        PASS = 1
        FAIL = 2
        WARNING = 3

    test_item = models.ForeignKey(TestItem, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    sentence = models.CharField(max_length=500)  # former sentences.translation
    label = models.IntegerField(
        choices=Label.choices, default=3
    )  # former sentences.pass


class TemplatePosition(models.Model):  # former templates
    template = models.ForeignKey(
        Template, on_delete=models.CASCADE
    )  # resolve from templates.id
    test_item = models.ForeignKey(
        TestItem, on_delete=models.CASCADE
    )  # resolve from templates.sentences
    pos = models.IntegerField()  # former templates.pos


class Distractor(models.Model):  # former distractors
    text = models.CharField(max_length=500)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)


class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    affiliation = models.CharField(max_length=100)
    occupation = models.CharField(max_length=100)
    reason = models.TextField()

    def __str__(self):
        return self.email
