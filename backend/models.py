from django.db import models
from languages.fields import LanguageField
# Create your models here.

## Bucket models
class BucketCategory(models.Model):
    name = models.CharField(max_length=25, primary_key=True)
    source_language = models.CharField(max_length=15)

class Bucket(models.Model):
    bucket_category = models.ForeignKey(BucketCategory, on_delete=models.CASCADE)
    description = models.CharField(max_length=100)

class BucketItem(models.Model):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE)
    token = models.CharField(max_length=30)

## Language pairs & Test Sets
class Langpair(models.Model):
    source_language = models.CharField(max_length=15)
    target_language = models.CharField(max_length=15)

class Testset(models.Model):
    description = models.CharField(max_length=250)

## from Categories to Rules
class Category(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    langpair = models.ForeignKey(Langpair, on_delete=models.CASCADE)

class Phenomenon(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)

class TestItem(models.Model):
    testset = models.ForeignKey(Testset, on_delete=models.CASCADE)
    phenomenon = models.ForeignKey(Phenomenon, on_delete=models.CASCADE)
    generation_time = models.DateField()
    source_sentence = models.CharField(max_length=1000)

class Rule(models.Model):
    item = models.ForeignKey(TestItem, on_delete=models.CASCADE)
    rule_string = models.CharField(max_length=200)
    prefix = models.BooleanField()
