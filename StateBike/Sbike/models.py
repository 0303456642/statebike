from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

#(general - could be Django's base User class?: no, we need DNI)
class DUser(models.Model): 
    user = models.OneToOneField(User)
    DNI = models.IntegerField(default=0)

class Client(DUser):
    tarjeta = models.IntegerField(default=0)
    def BuscarBici(self):
        pass
    def ChequearSancion(self):
        pass

#el nuevo admin es nuestro admin editado
class UserAdmin(UserAdmin):
    def MoverBicicleta(self):
        pass
    def CrearEstacion(self):
        pass


class Employee(DUser):
    def RepararBicicleta(self):
        pass

class Station(models.Model):
    Employee = models.ForeignKey(Employee)
    nombre = models.CharField(max_length=200)
    direccion = models.CharField(max_length=200)
    DNI = models.IntegerField(default=0)
    DNI = models.IntegerField(default=0)
    def QuitarDeStock(self):
        pass
    def AgregarDeStock(self):
        pass
    def BicicletaAReparar(self):
        pass

# convirtiendo nuestro admin a default UserAdmin
# real warning chequear si esto funciona
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
