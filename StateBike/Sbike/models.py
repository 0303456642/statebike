from django.db import models

# Create your models here.
class User(models.Model): #(general - could be Django's base User class?)
    nombre = models.CharField(max_length=200)
    DNI = models.IntegerField()
    password = models.CharField(max_length=200)

class Client(User):
    tarjeta = models.IntegerField()
    def BuscarBici(self):
        pass
    def ChequearSancion(self):
        pass

class Admin(User):
    def MoverBicicleta(self):
        pass
    def CrearEstacion(self):
        pass

class Employee(User):
    def RepararBicicleta(self):
        pass

class Station(models.Model):
    Employee = models.ForeignKey(Employee)
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    DNI = models.IntegerField()
    DNI = models.IntegerField()
    def QuitarDeStock(self):
        pass
    def AgregarDeStock(self):
        pass
    def BicicletaAReparar(self):
        pass
