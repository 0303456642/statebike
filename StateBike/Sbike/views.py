from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import IntegrityError

from .forms import ClientRegisterForm, ClientEditPhoneForm, ClientEditEmailForm
from .forms import ClientEditNameForm, ClientEditPasswordForm, ClientEditCardDataForm

from .models import Client
from .models import Admin
from .models import Employee
from .models import Station
from .models import Bike
from .models import Loan
from .models import Sanction

from random import randint # para las estaciones
from datetime import datetime, timedelta


###------------------------------------------------------------------------------------------------------------------------------------###
###---------------------------------------------------------REGISTER-------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###
def clientRegisterView(request):
    if request.user.is_authenticated():
        return redirect('/webprofile')

    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            username = cleaned_data.get('username')
            password = cleaned_data.get('password1')
            first_name = cleaned_data.get('first_name')
            last_name = cleaned_data.get('last_name')
            email = cleaned_data.get('email')
            phone_number = cleaned_data.get('phone_number')
            dni = cleaned_data.get('dni')
            card_number = cleaned_data.get('card_number')
            expiration_date = cleaned_data.get('expiration_date')
            security_code = cleaned_data.get('security_code')

            user = User.objects.create_user(username, email, password)

            user.first_name = first_name
            user.last_name = last_name

            user.save()

            client = Client()
            client.user = user
            client.phone_number = phone_number
            client.dni = dni

            client.edit_card(card_number, expiration_date, security_code)

            messages.success(request, 'You Have Successfully Registered')
            return redirect('/weblogin')

    else:
        form = ClientRegisterForm()
    context = {
        'form': form
    }
    return render(request, 'Sbike/client_register.html', context)
###------------------------------------------------------------------------------------------------------------------------------------###
###----------------------------------------------------END--REGISTER-------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###----------------------------------------------------------LOCATOR-------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###
@login_required
def locatorView(request):
    stations = Station.objects.all()
    return render(request, 'Sbike/stations.html', {'stations': stations})

###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------------END--LOCATOR-------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

###------------------------------------------------------------------------------------------------------------------------------------###
###----------------------------------------------------------HOME----------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


def home(request):
    logout(request)
    return render(request, 'Sbike/home.html')

###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------------END--HOME----------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------------WEB--LOGIN---------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

def webLoginView(request):
    if request.user.is_authenticated():
        return redirect('/webprofile')

    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['type'] = 'web'
                return redirect('/webprofile')
            else:
                message = 'Inactive User'
                return render(request, 'login.html', {'message': message})
        message = 'Invalid username/password'
    return render(request, 'Sbike/web_login.html', {'message': message})

###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------------WEB--LOGIN---------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------------STATION--LOGIN-----------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

def get_random_station():
    # asignar una estacion random
    stations = Station.objects.all()
    chosen = randint(0,len(stations) - 1)

    # seleccionar la estacion i-esima
    i = 0
    for st in stations:
        if i == chosen:
            break
        i = i + 1
    return st.id

def stationLoginView(request):
    if request.user.is_authenticated():
        return redirect('/stationprofile')

    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['station'] = get_random_station()
                request.session['type'] = 'station'
                return redirect('/stationprofile')
            else:
                message = 'Inactive User'
                return render(request, 'login.html', {'message': message})
        message = 'Invalid username/password'
    return render(request, 'Sbike/station_login.html', {'message': message})


###------------------------------------------------------------------------------------------------------------------------------------###
###------------------------------------------------END--STATION--LOGIN-----------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###------------------------------------------------------LOGOUT------------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

@login_required
def logoutView(request):
    
    messages.success(request, 'You have successfully logged out!')
    s_type = request.session['type']
    logout(request)
    if (s_type == 'station'): 
        return redirect('/stationlogin')
    return redirect('/weblogin')
###------------------------------------------------------------------------------------------------------------------------------------###
###------------------------------------------------------LOGOUT------------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

###------------------------------------------------------------------------------------------------------------------------------------###
###------------------------------------------------------STATION-PROFILE---------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


@login_required
def stationProfile(request):
    username = request.user.get_username()
    clients = Client.objects.filter(user__username=username)

    if len(clients) == 1:
        # create basic info dict
        dict = createUserDict(clients[0])

        # add extra client info
        dict['card_number'] = clients[0].card_number
        dict['exp_date'] = clients[0].expiration_date
        dict['sec_code'] = clients[0].security_code

        return render(request, 'Sbike/station_profile.html', dict)

    else:
        logout(request)
        messages.error(request, 'Admin/Employee can not login!')
        return redirect('/stationlogin')

###------------------------------------------------------------------------------------------------------------------------------------###
###-------------------------------------------------END--STATION-PROFILE---------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###----------------------------------------------------------WEB-PROFILE---------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

@login_required
def webProfile(request):

        username = request.user.get_username()
        clients = Client.objects.filter(user__username=username)
        admins = Admin.objects.filter(user__username=username)
        employees = Employee.objects.filter(user__username=username)

        if len(clients) == 1:
            return clientProfile(request, clients[0])

        elif len(admins) == 1:
                return adminProfile(request, admins[0])

        elif len(employees) == 1:
            return employeeProfile(request, employees[0])

#Esto que sigue ya no deberia volver a ocurrir.
#Si alguien lo detecta. Avise!!
        else:
            messages.error(request, 'Error: Access Denied')
            return redirect('/home')
###------------------------------------------------------------------------------------------------------------------------------------###
###------------------------------------------------------END--WEB--PROFILE-------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###------------------------------------------------------PROFILE--FUNCTS---------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


def clientProfile(request, client):

    # create basic info dict
    dict = createUserDict(client)

    # add extra client info
    dict['card_number'] = client.card_number
    dict['exp_date'] = client.expiration_date
    dict['sec_code'] = client.security_code

    return render(request, 'Sbike/client_profile.html', dict)


def adminProfile(request, admin):

    dict = createUserDict(admin)
    return render(request, 'Sbike/admin_profile.html', dict)


def employeeProfile(request, employee):

    dict = createUserDict(employee)
    return render(request, 'Sbike/employee_profile.html', dict)


def createUserDict(sbuser):

    dict = {}
    dict['fname'] = sbuser.user.first_name
    dict['lname'] = sbuser.user.last_name
    dict['username'] = sbuser.user.username
    dict['email'] = sbuser.user.email
    dict['dni'] = sbuser.dni
    dict['phone'] = sbuser.phone_number

    return dict

###------------------------------------------------------------------------------------------------------------------------------------###
###------------------------------------------------------PROFILE--FUNCTS---------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###--------------------------------------------------------LOANS-----------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


@login_required
def bikeLoan(request):
    if request.method == 'POST':

        client = Client.objects.get(user=request.user)
        try:
            bike_id = request.POST.get('select')
            bike = Bike.objects.get(id=bike_id)
            station = Station.objects.get(id=bike.station.id)
            loan = Loan()
            loan.create_loan(client, bike)

            # update data base after possible exception
            Bike.objects.filter(id=bike_id).update(state='TK')
            station.remove_from_stock()

            messages.success(request, 'Loan: Bike '+str(bike_id))
        except IntegrityError:
            messages.error(request, 'Sorry, You Have An Outstanding Loan')
        finally:
            return redirect('/stationprofile')
    bikes = Bike.objects.filter(state='AV',
                                station_id=request.session['station'])
    if len(bikes) == 0:
        messages.error(request, 'Sorry, No Bikes Available!')
    return render(request, 'Sbike/bike_loan.html', ({'bikes': bikes}))

###------------------------------------------------------------------------------------------------------------------------------------###
###--------------------------------------------------------END--LOANS------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###--------------------------------------------------------GIVE--BACK------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

@login_required
def givebackView(request):
    station = Station.objects.get(id=request.session['station'])
    if request.method == 'POST':
        bike_id = request.POST.get('select')
        Bike.objects.filter(id=bike_id).update(state='AV')
        bike = Bike.objects.get(id=bike_id)
        station.add_to_stock()

        loan = Loan.objects.get(bike=bike_id)
        loan.set_end_date()
        days = loan.eval_sanction()

        if days > 0:
            sanction = Sanction()
            sanction.create_sanction(loan, days)
        else:
            Loan.objects.filter(bike=bike_id).delete()

        message = 'Thanks For Return!'
        return render(request, 'Sbike/give_back.html', {'message': message})

    # check if there is capacity available
    if station.stock >= station.capacity:
        messages.error(request, 'Sorry! There is no capacity in the station %s' % station.name)
        return render(request, 'Sbike/give_back.html')
    client = Client.objects.get(user=request.user)
    try:
        loan = Loan.objects.get(client=client)
        bike = Bike.objects.get(id=loan.bike.id)
        return render(request, 'Sbike/give_back.html', {'bike': bike})
    except ObjectDoesNotExist:
        messages.error(request, 'Sorry! No Loans Outstanding!!')
        return render(request, 'Sbike/give_back.html')

###------------------------------------------------------------------------------------------------------------------------------------###
###---------------------------------------------------END--GIVE--BACK------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###---------------------------------------------------EDIT---PASSWORD------------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


@login_required
def clientEditPassword(request):
    client = Client.objects.get(user=request.user)
    if request.method == 'POST':
        form = ClientEditPasswordForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            """comprueba cada campo que no este vacio"""
            """si no lo esta entonces modifica la base"""

            password = make_password(cleaned_data['password1'])
            if password:
                client.user.password = password
                messages.success(request, 'Password Changed Successfully')
            else:
                messages.error(request, 'Error! Password Null!')
            client.user.save()
            return redirect('/webprofile')

    form = ClientEditPasswordForm()
    context = {
        'form': form
    }
    return render(request, 'Sbike/client_edit.html', context)


###------------------------------------------------------------------------------------------------------------------------------------###
###-------------------------------------------------END--EDIT--PASSWORD----------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


###------------------------------------------------------------------------------------------------------------------------------------###
###------------------------------------------------EDIT--CLIENT--CARD--DATA------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###


@login_required
def clientEditCardData(request):
    
    client = Client.objects.get(user=request.user)
    if request.method == 'POST':
        form = ClientEditCardDataForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            """comprueba cada campo que no este vacio""" 
            """si no lo esta entonces modifica la base"""
            card_number = cleaned_data['card_number']
            expiration_date = cleaned_data['expiration_date']
            security_code = cleaned_data['security_code']

            client.edit_card(card_number, expiration_date, security_code)

            messages.success(request, 'Successfully Update!')
            return redirect('/editprofile/card')
    form = ClientEditCardDataForm()
    context = {
        'form' : form
    }
    return render(request, 'Sbike/client_edit.html', context)

###------------------------------------------------------------------------------------------------------------------------------------###
###---------------------------------------------END--EDIT--CLIENT--CARD--DATA----------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###



###------------------------------------------------------------------------------------------------------------------------------------###
###-------------------------------------------------EDIT--CLIENT--PHONE----------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###
@login_required
def ClientEditPhone(request):
    client = Client.objects.get(user=request.user)

    if request.method == 'POST':
        form = ClientEditPhoneForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            phone_number = cleaned_data['phone_number']
            client.edit_phone(phone_number)
            messages.success(request, 'Successfully Update! Phone: '+ str(phone_number))
            return redirect('/editprofile/phone')
    
    form = ClientEditPhoneForm()
    context = {
        'form' : form
    }
    return render(request, 'Sbike/client_edit.html',context)



###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------END--EDIT--CLIENT--PHONE-------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

###------------------------------------------------------------------------------------------------------------------------------------###
###--------------------------------------------------EDIT--CLIENT--EMAIL---------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###



@login_required
def ClientEditEmail(request):
    client = Client.objects.get(user=request.user)

    if request.method == 'POST':
        form = ClientEditEmailForm(request.POST)
        if form.is_valid():
            email = form.clean_email()
            client.edit_email(email)
            messages.success(request, 'Successfully Update! Email: '+ str(email))
            return redirect('/editprofile/email')
    
    form = ClientEditEmailForm()
    context = {
        'form' : form
    }
    return render(request, 'Sbike/client_edit.html',context)


###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------END--EDIT--CLIENT--EMAIL-------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###
