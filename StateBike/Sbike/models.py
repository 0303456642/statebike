from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class SBikeUser(models.Model):
    user = models.OneToOneField(User)

    dni = models.IntegerField(blank=False, primary_key=True)
    phone_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "DNI: " + str(self.dni)


class Client(SBikeUser):
    card_number = models.IntegerField(blank=False, null=True)
    expiration_date = models.DateField(blank=False, null=True)
    security_code = models.IntegerField(blank=False, null=True)

    def edit_card(self, card_number, expiration_date, security_code):
        self.card_number = card_number
        self.expiration_date = expiration_date
        self.security_code = security_code
        self.save()

class Admin(SBikeUser):
    pass


class Employee(SBikeUser):
    pass


class Station(models.Model):
    employee = models.ForeignKey(Employee)

    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    stock = models.IntegerField(blank=False)
    capacity = models.IntegerField(blank=False)

    def __str__(self):
        return str(self.name)

    def remove_from_stock(self):
        self.stock = self.stock - 1
        self.save()

    def add_to_stock(self):
        self.stock = self.stock + 1
        self.save()


class Bike(models.Model):
    AVAILABLE = 'AV'
    TAKEN = 'TK'
    BROKEN = 'BR'

    STATE_CHOICES = (
        (AVAILABLE, 'Available'),
        (TAKEN, 'Taken'),
        (BROKEN, 'Broken'),
    )

    state = models.CharField(
        max_length=2, choices=STATE_CHOICES,
        default=AVAILABLE)

    station = models.ForeignKey(Station)

    def __str__(self):
        return "Bike: " + str(self.id)

    def take(self):
        self.state = 'TK'
        self.save()

    def repair(self):
        self.state = 'AV'
        self.save()

    def give_back(self):
        self.state = 'AV'
        self.save()


class Loan(models.Model):
    client = models.OneToOneField(Client)
    bike = models.OneToOneField(Bike)
    startDate = models.DateTimeField(default=datetime.now)
    endDate = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)

    def __str__(self):
        return "Loan: " + str(self.id)

    def create_loan(self,):
        self.client = client
        self.bike = bike
        self.save()

    def eval_sanction(self):
        pass


class Sanction(models.Model):
    loan = models.OneToOneField(Loan)
    amount = models.DecimalField(max_digits=, decimal_places=2, null=True, blank=True)
    under = models.CharField(max_length=100)
    date = models.DateTimeField(null=True, blank=True)
    deposition = models.TextField(null=True, blank=True)

    def __set_under(self, under):
        self.under = under
        self.save()

    def create_sanction(self, loan, amount, under, date):
        self.__set_under(under)
        self.loan = loan
        self.amount = amount
        self.date = date
        self.save()

    def generate_deposition(self, deposition):
        self.deposition = deposition
        self.save()
