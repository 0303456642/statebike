from django.db import models

# Create your models here.
class User(models.Model): #(general - could be Django's base User class?)
    nombre = models.CharField(max_length=200)
    DNI = models.IntegerField()
    password = models.CharField(max_length=200)
class Client(User):
    tarjeta = models.IntegerField()
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
class Admin(User):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
class Employee(User):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
class Station(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    models.DateTimeField('date published')
