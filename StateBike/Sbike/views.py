from django.shortcuts import render
from django.contrib.auth.models import User
from .forms import ClientRegisterForm
from .models import Client

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

	else:
		form = ClientRegisterForm()
	context = {
		'form' : form
	}
	return render(request, 'Sbike/client_register.html', context)