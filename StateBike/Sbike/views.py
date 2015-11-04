from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from .forms import ClientRegisterForm
from .models import Client
from .models import Admin
from .models import Employee
from .models import Station

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def principal(req):
    return render(req, 'Sbike/index.html')

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
            return redirect('/weblogin')

    else:
        form = ClientRegisterForm()
    context = {
        'form' : form
    }
    return render(request, 'Sbike/client_register.html', context)

def locatorView(request):
    stations = Station.objects.all()
    return render(request, 'Sbike/stations.html', {'stations':stations})

def homePrinc(request):
    return render(request,'Sbike/homePrinc.html')

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
                message = 'El usuario ingresado se encuentra inactivo.'
                return render(request, 'login.html', {'message' : message})
        message = 'Nombre de usuario y/o password invalidos'
    return render(request, 'Sbike/web_login.html', {'message' : message})

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
                message = 'El usuario ingresado se encuentra inactivo.'
                return render(request, 'login.html', {'message' : message})
        message = 'Nombre de usuario y/o password invalidos'
    return render(request, 'Sbike/station_login.html', {'message' : message})

def morir():
    return HttpResponse('estas muerto')

def webProfile(req):
    # if it's authenticated, load the corresponding profile
    if req.user.is_authenticated():
        username = req.user.get_username()
        clients = Client.objects.filter(user__username=username)
        admins = Admin.objects.filter(user__username=username)
        employees = Employee.objects.filter(user__username=username)

        if len(clients) == 1:
            return clientProfile(req, clients[0])


        elif len(admins) == 1 or username == 'admin':
            if len(admins) == 0:
                return HttpResponse('Usted es el admin de django. <a href="../logout">Cerrar Sesion</a>')
            else:
                return adminProfile(req, admins[0])


        elif len(employees) == 1:
            return employeeProfile(req, employees[0])


        else:
            return HttpResponse('Error: Hay un usuario logueado inexistente en la base de datos o varios usuarios comparten el mismo username "%s"' % username)
    # if it's not authenticated, send to login
    else:
        return redirect('/weblogin')


def clientProfile(req, client):

    # create basic info dict
    dict = createUserDict(client)

    # add extra client info
    dict['card_number'] = client.card_number
    dict['exp_date'] = client.expiration_date
    dict['sec_code'] = client.security_code

    return render(req, 'Sbike/client_profile.html', dict)

def adminProfile(req, admin):

    dict = createUserDict(admin)
    return render(req, 'Sbike/admin_profile.html', dict)

def employeeProfile(req, employee):

    dict = createUserDict(employee)
    return render(req, 'Sbike/employee_profile.html', dict)

def createUserDict(sbuser):

    dict = {}
    dict['fname'] = sbuser.user.first_name
    dict['lname'] = sbuser.user.last_name
    dict['username'] = sbuser.user.username
    dict['email'] = sbuser.user.email
    dict['dni'] = sbuser.dni
    dict['phone'] = sbuser.phone_number

    return dict


@login_required
def locatorView(request):
    stations = Station.objects.all()
    return render(request, 'Sbike/stations.html', {'stations':stations})

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
                message = 'El usuario ingresado se encuentra inactivo.'
                return render(request, 'login.html', {'message' : message})
        message = 'Nombre de usuario y/o password invalidos'
    return render(request, 'Sbike/web_login.html', {'message' : message})

def stationLoginView(request):
    if request.user.is_authenticated():
        return redirect('/stationProfile')

    message = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/stationProfile')
            else:
                message = 'El usuario ingresado se encuentra inactivo.'
                return render(request, 'login.html', {'message' : message})
        message = 'Nombre de usuario y/o password invalidos'
    return render(request, 'Sbike/station_login.html', {'message' : message})

@login_required
def logoutView(request):
    logout(request)
    messages.success(request, 'You have successfully logged out!')
    return redirect('/weblogin')
