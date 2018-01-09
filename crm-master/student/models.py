from django.db import models

# Create your models here.
class SProvince(models.Model):
    name = models.CharField(max_length=32,)

class SCity(models.Model):
    name = models.CharField(max_length=32)
    pro = models.ForeignKey("SProvince")


class Book(models.Model):
    name = models.CharField(max_length=32)

class Author(models.Model):
    name = models.CharField(max_length=32)
    m = models.ManyToManyField('Book')
