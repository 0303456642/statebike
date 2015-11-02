from django.db import models
from django.contrib.auth.models import User

class SBikeUser(models.Model):
     user = models.OneToOneField(User)

     dni = models.IntegerField(blank=False, primary_key=True)
     phone_number = models.IntegerField(null=True, blank=True)

     def  __str__(self):
        return self.dni

class Client(SBikeUser):
     card_number = models.IntegerField(blank=False, null=True)
     expiration_date = models.DateField(blank=False, null=True)
     security_code = models.IntegerField(blank=False, null=True)
     def findStation(self):
         pass
     def checkPenalty(self):
         pass

class Admin(SBikeUser):
     def moveBikes(self):
         pass
     def createStation(self):
         pass
     def createBike(self):
         pass

class Employee(SBikeUser):
    def repairBike(self):
        pass

class Station(models.Model):
    employee = models.ForeignKey(Employee)

    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    stock = models.IntegerField(blank=False)
    capacity = models.IntegerField(blank=False)

    def removeFromStock(self):
        pass
    def addToStock(self):
        pass
    def bikesToRepair(self):
        pass
