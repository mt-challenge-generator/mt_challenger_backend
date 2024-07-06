from django.db import models


class Language(models.Model):
    code = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.name

class Langpair(models.Model):
    source_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="source_language"
    )
    target_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="target_language"
    )
    def __str__(self):
        return f"{self.source_language} to {self.target_language}"  
     
class Testset(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=250)
    langpair = models.ForeignKey(Langpair, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Category(models.Model):  # values from rules.category
    name = models.CharField(max_length=30)
    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name

class Phenomenon(models.Model):  # values from rules.barrier
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    class Meta:
        verbose_name_plural = "Phenomena"
    def __str__(self):
        return self.name

class TestItem(models.Model):  # former rules
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.CharField(max_length=10, blank=True, null=True )  # former rules.ID
    legacy_testpoint = models.SmallIntegerField(blank=True, null=True)  # former rules.testPoint
    legacy_version = models.SmallIntegerField(blank=True, null=True)  # former rules.version
    testset = models.ForeignKey(Testset, on_delete=models.CASCADE)
    phenomenon = models.ForeignKey(
        Phenomenon, on_delete=models.CASCADE
    )  # resolve from rules.barrier
    source_sentence = models.CharField(max_length=500)  # former rules.source
    comment = models.CharField(max_length=100)  # former rules.comment
    created_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.source_sentence
    
class Rule(models.Model):
    id = models.BigAutoField(primary_key=True)
    item = models.ForeignKey(TestItem, on_delete=models.CASCADE)
    string = models.CharField(max_length=200)
    regex = models.BooleanField(default=True)
    positive = models.BooleanField(default=True)
    
    def __str__(self):
        return self.string
    
class Template(models.Model):  # former template_meta
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.SmallIntegerField(
        blank=True, null=True
    )  # former template_meta.id
    testset = models.ForeignKey(Testset, on_delete=models.CASCADE)
    
    name = models.CharField(max_length=50, blank=True)
    select = models.DecimalField(
        max_digits=10, decimal_places=2
    )  
    phenomena = models.ManyToManyField(Phenomenon)  # resolve from template_meta.from
    categories = models.ManyToManyField(Category)  # resolve from template_meta.from
    scramble_factor = models.DecimalField(
        max_digits=5, decimal_places=1
    )  # former template_meta.meta.scramble_factor
    created_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Template ID: {self.id}"

class Report(models.Model):  # former reports
    id = models.BigAutoField(primary_key=True)
    legacy_id = models.SmallIntegerField(blank=True, null=True)  # former reports.id
    template = models.ForeignKey(
        Template, on_delete=models.CASCADE
    )  # resolve from reports.templateid
    engine = models.CharField(max_length=50 ,blank=True, null=True)  
    engine_type = models.CharField(max_length=50 ,blank=True, null=True)
    comment = models.CharField(max_length=100 ,blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)  # former reports.time

    def __str__(self):
        return f"Report {self.id}"

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

    def __str__(self):
        return f"Translation for {self.test_item}"
    
class TemplatePosition(models.Model):  # former templates
    template = models.ForeignKey(
        Template, on_delete=models.CASCADE
    )  # resolve from templates.id
    test_item = models.ForeignKey(
        TestItem, on_delete=models.CASCADE
    )  # resolve from templates.sentences
    pos = models.IntegerField()  # former templates.pos

    def __str__(self):
        return f"Position {self.pos} in template {self.template_id}"
    
class Distractor(models.Model):  # former distractors
    text = models.CharField(max_length=500)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.text