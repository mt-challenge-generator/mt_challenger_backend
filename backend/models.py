from django.db import models

# Create your models here.

## Bucket models
class Bucket_category(models.Model):
    name = models.CharField(max_length=25, primary_key=True)
    source_language = models.CharField(max_length=15)

class Bucket(models.Model):
    bucket_categoryid = models.ForeignKey(Bucket_Category, on delete=models.CASCADE)
    description = models.CharField(max_length=100)

class Bucket_item(models.Model):
    bucket_id = models.ForeignKey(Bucket, on delete=models.CASCADE)
    token = models.CharField(max_length=30)

## Language pairs & Test Sets
class Langpair(models.Model):
    source_language = models.CharField(max_length=15)
    target_language = models.CharField(max_length=15)

class Testset(models.Model):
    description = models.CharField(max_length=250)

## from Categories to Rules
class Category(models.Model):
    langpair_id = models.ForeignKey(Langpair, on delete=models.CASCADE)
    name = models.CharField(max_length=30, primary_key=True)

class Phenomenon(models.Model):
    category_id = models.ForeignKey(Category, on delete=models.CASCADE)
    name = models.CharField(max_length=30)

class Test_item(models.Model):
    testset_id = models.ForeignKey(Testset, on delete=models.CASCADE)
    phenomenon_id = models.ForeignKey(Phenomenon, on delete=models.CASCADE)
    generation_time = models.DateField()
    source_sentence = models.CharField(max_length=1000)

class Rule(models.Model):
    item_id = models.ForeignKey(Test_item, on delete=models.CASCADE)
    rule_string = models.CharField(max_length=200)
    prefix = models.BooleanField()
