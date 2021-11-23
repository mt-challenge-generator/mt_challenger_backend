from django.db import models

# Create your models here.

class Bucket_category(models.Model):
    name = models.CharField(max_length=25, primary_key=True)

class Bucket(models.Model):
    bucket_categoryid = models.ForeignKey(Bucket_Category, on delete=models.CASCADE)
    description = models.CharField(max_length=100)
    

class Bucket_item(models.Model):
    bucket_id = models.ForeignKey(Bucket, on delete=models.CASCADE)
    token = models.CharField(max_length=30)
