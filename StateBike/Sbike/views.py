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
            client.card_number = card_number
            client.expiration_date = expiration_date
            client.security_code = security_code

            client.save()
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
    logout(request)
    messages.success(request, 'You have successfully logged out!')
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
            Bike.objects.filter(id=bike_id).update(state='TK')
            bike = Bike.objects.get(id=bike_id)
            station = Station.objects.get(id=bike.station.id)
            station.remove_from_stock()
            loan = Loan()
            loan.client = client
            loan.bike = bike
            loan.save()

            messages.success(request, 'Loan: Bike '+str(bike_id))
        except IntegrityError:
            messages.error(request, 'Sorry, You Have An Outstanding Loan')
        finally:
            return redirect('/stationprofile')
    bikes = Bike.objects.filter(state='AV')
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
    if request.method == 'POST':
        bike_id = request.POST.get('select')
        Bike.objects.filter(id=bike_id).update(state='AV')
        bike = Bike.objects.get(id=bike_id)
        station = Station.objects.get(id=bike.station.id)
        station.add_to_stock()
        Loan.objects.filter(bike=bike_id).delete()
        message = 'Thanks For Return!'
        return render(request, 'Sbike/give_back.html', {'message': message})
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
            return redirect('/weblogin')

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
    name = request.user.get_username()
    current = Client.objects.get(user__username = name)
    if request.method == 'POST':
        form = ClientEditCardDataForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            """comprueba cada campo que no este vacio""" 
            """si no lo esta entonces modifica la base"""
            card_number = cleaned_data['card_number']
            expiration_date = cleaned_data['expiration_date']
            security_code = cleaned_data['security_code']

            current.card_number = card_number
            current.expiration_date = expiration_date
            current.security_code = security_code
            current.save()
            return redirect('/webprofile')
    form = ClientEditCardDataForm()
    context = {
        'form' : form
    }
    return render(request, 'Sbike/client_edit.html',context)

###------------------------------------------------------------------------------------------------------------------------------------###
###---------------------------------------------END--EDIT--CLIENT--CARD--DATA----------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###



###------------------------------------------------------------------------------------------------------------------------------------###
###-------------------------------------------------EDIT--CLIENT--PHONE----------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###
@login_required
def ClientEditPhone(request):
    name = request.user.get_username()
    current = Client.objects.get(user__username = name)
    if request.method == 'POST':
        form = ClientEditPhoneForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            phone_number = cleaned_data['phone_number']
            current.phone_number = phone_number
            current.save()
            return redirect('/webprofile')
    
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
    name = request.user.get_username()
    current = Client.objects.get(user__username = name)
    if request.method == 'POST':
        form = ClientEditEmailForm(request.POST)
        if form.is_valid():
            email = form.clean_email()
            current.user.email = email
            current.user.save()
            return redirect('/webprofile')
    
    form = ClientEditEmailForm()
    context = {
        'form' : form
    }
    return render(request, 'Sbike/client_edit.html',context)


###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------END--EDIT--CLIENT--EMAIL-------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

###------------------------------------------------------------------------------------------------------------------------------------###
###--------------------------------------------------EDIT--CLIENT--NAME-----------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

def ClientEditName(request):
    name = request.user.get_username()
    current = Client.objects.get(user__username = name)
    if request.method == 'POST':
        form = ClientEditNameForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            first_name = cleaned_data['first_name']
            last_name = cleaned_data['last_name']

            current.user.first_name = first_name
            current.user.last_name = last_name
            current.user.save()
            return redirect('/webprofile')
    
    form = ClientEditNameForm()
    context = {
        'form' : form
    }
    return render(request, 'Sbike/client_edit.html',context)



###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------END--EDIT--CLIENT--NAME---------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

###------------------------------------------------------------------------------------------------------------------------------------###
###--------------------------------------------------EDIT--CLIENT--PAGE----------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###

@login_required
def clientEditDataPage(request):
    name = request.user.get_username()
    current = Client.objects.get(user__username = name)
    if not(current is None):
        # create basic info dict
        dict = createUserDict(current)

        # add extra client info
        dict['card_number'] = current.card_number
        dict['exp_date'] = current.expiration_date
        dict['sec_code'] = current.security_code

    return render(request, 'Sbike/client_what_edit.html', dict)

###------------------------------------------------------------------------------------------------------------------------------------###
###-----------------------------------------------END--EDIT--CLIENT--PAGE--------------------------------------------------------------###
###------------------------------------------------------------------------------------------------------------------------------------###
