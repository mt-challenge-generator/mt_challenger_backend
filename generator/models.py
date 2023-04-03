from django.db import models

from evaluator.models import Language


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
