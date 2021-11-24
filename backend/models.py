from django.db import models
from django.db.models import BigAutoField


class Language(models.Model):
    code = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=30)


# Bucket models
class BucketCategory(models.Model):
    name = models.CharField(max_length=25)
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "BucketCategories"


class Bucket(models.Model):
    bucket_category = models.ForeignKey(BucketCategory, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)


class BucketItem(models.Model):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    token = models.CharField(max_length=30)


# Language pairs & Test Sets

class Langpair(models.Model):
    source_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='source_language')
    target_language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='target_language')


class Testset(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=250)


# from Categories to Rules
class Category(models.Model):
    name = models.CharField(max_length=30)
    langpair = models.ForeignKey(Langpair, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Categories"


class Phenomenon(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Phenomena"


class TestItem(models.Model):
    testset = models.ForeignKey(Testset, on_delete=models.CASCADE)
    phenomenon = models.ForeignKey(Phenomenon, on_delete=models.CASCADE)
    generation_time = models.DateField(null=True)
    source_sentence = models.CharField(max_length=1000)


class Rule(models.Model):
    item = models.ForeignKey(TestItem, on_delete=models.CASCADE)
    rule_string = models.CharField(max_length=200)
    prefix = models.BooleanField()
