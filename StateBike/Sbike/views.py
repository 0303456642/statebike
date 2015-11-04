from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from .forms import ClientRegisterForm
from .models import Client
from .models import Station

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def clientRegisterView(request):
	if request.method == 'POST':
		form = ClientRegisterForm(request.POST)


		if form.is_valid():
			cleaned_data = form.cleaned_data

			username = cleaned_data.get('username')
			password = cleaned_data.get('password')

			first_name = cleaned_data.get('first_name')
			last_name = cleaned_data.get('last_name')
			email = cleaned_data.get('email')
			phone_number = cleaned_data.get('phone_number')
			dni = cleaned_data.get('dni')
			card_number = cleaned_data.get('card_number')
			expiration_date = cleaned_data.get('expiration_date')
			security_code = cleaned_data.get('security_code')

			user = User.objects.create_user(username=username, password=password)

			user.first_name = first_name
			user.last_name = last_name
			user.email = email

			user.save()


			client = Client()

			client.user = user
			client.phone_number = phone_number
			client.dni = dni
			client.card_number = card_number
			client.expiration_date = expiration_date
			client.security_code = security_code

			client.save()
			return redirect(reverse('welcome', kwargs={'username':username}))

	else:
		form = ClientRegisterForm()
	context = {
		'form' : form
	}
	return render(request, 'Sbike/client_register.html', context)


def welcomeNewClientView(request, username):
	return render(request, 'Sbike/welcome.html', {'username': username})

def locatorView(request):
	stations = Station.objects.all()
	return render(request, 'Sbike/stations.html', {'stations':stations})

def webLoginView(request):
	if request.user.is_authenticated():
		return redirect('Sbike.views.webProfile')

	message = ''
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('Sbike.views.webProfile')
			else:
				message = 'El usuario ingresado se encuentra inactivo.'
				return render(request, 'login.html', {'message' : message})
		message = 'Nombre de usuario y/o password invalidos'
	return render(request, 'Sbike/web_login.html', {'message' : message})

def stationLoginView(request):
	if request.user.is_authenticated():
		return redirect('Sbike.views.stationProfile')

	message = ''
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect('Sbike.views.stationProfile')
			else:
				message = 'El usuario ingresado se encuentra inactivo.'
				return render(request, 'login.html', {'message' : message})
		message = 'Nombre de usuario y/o password invalidos'
	return render(request, 'Sbike/station_login.html', {'message' : message})
