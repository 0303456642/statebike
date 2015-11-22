# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from Sbike import views
from django.contrib.auth.models import User
from .models import Client as OurClient, Admin, Employee, Station
import os, re

# Create your tests here.

APP_NAME = 'Sbike'

class Accesos(TestCase):

    formValid = {
        'username' : 'pepeloco',
        'password1' : 'pepeelmascapo',
        'password2' : 'pepeelmascapo',
        'first_name' : 'Pepe',
        'last_name' : 'Loco',
        'email' : 'pepe@loco.com',
        'phone_number' : '3511234567',
        'dni' : '0303456',
        'card_number' : '938765451673',
        'expiration_date' : '2015-05-30',
        'security_code' : '642'
    }

    templates = {
        'home' : 'home.html',
        'register' : 'client_register.html',
        'weblogin' : 'web_login.html',
        'stationlogin' : 'station_login.html',
        'clientprofile' : 'client_profile.html',
        'stationprofile' : 'station_profile.html',
        'stations' : 'stations.html'
    }

    def test_home(self):
        c = Client()
        res = c.get('/')

        # deberia devolver la home page
        self.assertTrue(self.is_template(res, self.templates['home']))

    def test_obtener_registro(self):
        """ Intentamos obtener el formulario de registro """
        # creamos un cliente
        c = Client()
        # follow es para seguir los redireccionamientos
        res = c.get('/register', follow = True)

        # deberia devolver la register page
        self.assertTrue(self.is_template(res, self.templates['register']))

    def test_register_user(self):
        """ Intentamos registrarnos """
        c = Client()
        # Creamos un formulario invalido y lo intentamos enviar

        form = {
            'username' : 'a'
        }
        res = c.post('/register/', form, follow = True)

        # deberiamos obtener otra vez la pagina de registro
        self.assertTrue(self.is_template(res, self.templates['register']))
        
        # Ahora cramos un formulario valido
        res = c.post('/register/', self.formValid, follow = True)

        # deberiamos obtener el login
        self.assertTrue(self.is_template(res, self.templates['weblogin']))

        # y recibir el msj de exito
        try:
            res.content.index('You Have Successfully Registered')
        except ValueError:
            self.fail('Mensaje de exito no encontrado')

    def test_weblogin(self):
        """ Intentamos loguearnos (in)validamente """

        c = Client()

        # Intentamos obtener la pagina de login
        res = c.get('/weblogin', follow=True)
        self.assertTrue(self.is_template(res, self.templates['weblogin']))

        # Nos intentamos loguear con un usuario inexistente
        res = c.post('/weblogin/', {'username': 'probablementeningunusuarioexistaconestenombre',
                                    'password': 'miranda'}, follow=True)

        # Nos deberia volver a llevar al login
        self.assertTrue(self.is_template(res, self.templates['weblogin']))

        # Con un mensaje de error
        try:
            res.content.index('Invalid username')
        except ValueError:
            self.fail('Mensaje de error no encontrado')


        # ahora nos registramos 
        res = c.post('/register/', self.formValid, follow = True)        

        # deberiamos obtener el weblogin
        self.assertTrue(self.is_template(res, self.templates['weblogin']))

        # y recibir el msj de exito
        try:
            res.content.index('You Have Successfully Registered')
        except ValueError:
            self.fail('Mensaje de exito no encontrado')

        # y ahora intentamos loguearnos bien
        res = c.post('/weblogin/', {'username': self.formValid['username'],
                                    'password': self.formValid['password1']}, follow=True)

        # deberia llevarnos al perfil nuestro
        self.assertTrue(self.is_template(res, self.templates['clientprofile']))

        # revisemos que nuestro username este en el perfil
        try:
            res.content.index(self.formValid['username'])
        except ValueError:
            self.fail('Mi username no estaba en mi perfil')

        # y si tratamos de ir a la pagina de login (ya logueados)
        res = c.get('/weblogin', follow=True)

        # deberia llevarnos al perfil nuestro
        self.assertTrue(self.is_template(res, self.templates['clientprofile']))

        # revisemos que nuestro username este en el perfil
        try:
            res.content.index(self.formValid['username'])
        except ValueError:
            self.fail('Mi username no estaba en mi perfil')


    def test_stationlogin(self):
        """ intento de inicio de sesion en la estacion """

        c = Client()

        # Creamos una estacion
        self.createStation('San Martin', self.createEmployee('carlos123', 'carlitos'))

        # Intentamos obtener la pagina de login
        res = c.get('/stationlogin', follow=True)
        self.assertTrue(self.is_template(res, self.templates['stationlogin']))

        # Nos intentamos loguear con un usuario inexistente
        res = c.post('/stationlogin/', {'username': 'probablementeningunusuarioexistaconestenombre', 'password': 'miranda'}, follow=True)

        # No deberia dejarnos pasar
        self.assertTrue(self.is_template(res, self.templates['stationlogin']))

        # ahora nos registramos 
        res = c.post('/register/', self.formValid, follow = True)

        # y ahora intentamos loguearnos bien
        res = c.post('/stationlogin/', {'username': self.formValid['username'], 'password': self.formValid['password1']}, follow=True)

        # deberia llevarnos al perfil de la estacion
        self.assertTrue(self.is_template(res, self.templates['stationprofile']))


    def test_view_stations(self):
        """ Intento de ver estaciones con y sin autenticacion """

        c = Client()

        # intentemos ver las estaciones sin login
        res = c.get('/stations', follow=True)

        # deberiamos terminar en el weblogin
        self.assertTrue(self.is_template(res, self.templates['weblogin']))

        # nos registramos y logueamos
        res = c.post('/register/', self.formValid, follow = True)
        c.login(username=self.formValid['username'], password=self.formValid['password1'])

        # ahora re-intentamos
        res = c.get('/stations', follow=True)

        # deberiamos terminar en stations
        self.assertTrue(self.is_template(res, self.templates['stations']))

    def test_logout(self):
        """ Inicio y cierre de sesion """

        c = Client()

        # Creamos una estacion
        self.createStation('San Martin', self.createEmployee('carlos123', 'carlitos'))

        # nos registramos
        res = c.post('/register/', self.formValid, follow = True)

        # nos logueamos en la estacion
        res = c.post('/stationlogin/',
                     {'username': self.formValid['username'],
                      'password': self.formValid['password1']},
                     follow=True)

        # si salio bien estamos en el station profile
        self.assertTrue(self.is_template(res, self.templates['stationprofile']))

        # cerramos sesion
        res = c.get('/logout', follow = True)

        # deberiamos terminar en la pagina de station login
        self.assertTrue(self.is_template(res, self.templates['stationlogin']))

        # nos logueamos en weblogin
        res = c.post('/weblogin/',
                     {'username': self.formValid['username'],
                      'password': self.formValid['password1']},
                     follow=True)

        # si salio bien estamos en el web profile
        self.assertTrue(self.is_template(res, self.templates['clientprofile']))

        # cerramos sesion
        res = c.get('/logout', follow = True)

        # deberiamos terminar en la pagina de station login
        self.assertTrue(self.is_template(res, self.templates['weblogin']))


    def createStation(self, name, empl):

        station = Station()
        station.create_station(empl, name, name+ '  123', 5, 10)

        return station

    def createEmployee(self, username, passw):

        user = User.objects.create_user(username, '', passw)

        user.first_name = 'Carlos'
        user.last_name = 'Bederian'

        empl = Employee()
        empl.user = user
        empl.phone_number = '49291'
        empl.dni = '18999333'

        empl.save()

        return empl

    def createAdmin(self, username, passw):

        user = User.objects.create_user(username, '', passw)

        user.first_name = 'Carlos'
        user.last_name = 'Bederian'

        user.save()

        admin = Admin()
        admin.user = user
        admin.phone_number = '351123999'
        admin.dni = '17282282'

        admin.save()

        return admin

    def debug(self, res):
        """ Vos le pasas el res y debug te banca """

        print('\nEstado: ' + str(res.status_code))
        print('Redirecciones: ' + str(res.redirect_chain))

        known = False
        for templ in self.templates:
            if self.is_template(res, self.templates[templ]):
                known = True
                print('Página "' + templ + '" recibida.')
                break

        if not known:
            print('Página no conocida')

        f = open('respuesta.html', 'w')
        f.write(res.content)
        print('Respuesta guardada en "respuesta.html"')

    def is_template(self, res, filename, details=False):
        titles_match = self.titles_match(res, filename, details)

        # aca podrian haber otros chequeos ademas de los titulos

        return titles_match

    def titles_match(self, res, templ, details=False):

        template_title = self.get_template_title(templ)
        title_reg = reg_from_template(template_title)

        template_h1 = self.get_template_h1(templ)
        h1_reg = reg_from_template(template_h1)

        bar_title_matchs = title_reg.match(self.get_content_title(res.content))

        h1_title_matchs = h1_reg.match(self.get_content_h1(res.content))

        if details:
            print('bar content: "'+ str(self.get_content_title(res.content)) +'"')
            print('bar template: "'+str(self.get_template_title(templ))+'"')
            print('bar regexp template: "' + title_reg.pattern + '"')

            print('h1 content: "'+ str(self.get_content_h1(res.content)) +'"')
            print('h1 template: "'+str(self.get_template_h1(templ))+'"')
            print('h1 regexp template: "' + h1_reg.pattern + '"')

        return bar_title_matchs and h1_title_matchs


    def get_template_h1(self, templ):
        return get_template_string(templ, '<h1>', '</h1>')

    def get_content_h1(self, cont):
        return find_between(cont, '<h1>', '</h1>')

    def get_template_title(self, templ):
        return get_template_string(templ, '{% block title %}', '{% endblock title %}')

    def get_content_title(self, cont):
        return find_between(cont, '<title>', '</title>')



def get_template_string(templ, string1, string2):
    f =  open(APP_NAME + '/' + templ, 'r')
    template = f.read()

    return find_between(template, string1, string2)

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)

        string = s[start:end]
        if string[0] == ' ':
            string = string[1:]
        if string[-1] == ' ':
            string = string[:-1]

        return string

    except ValueError:
        return ""


def reg_from_template(string):
    regexp = string
    while True:
        try:
            start = regexp.index('{{')
            end = regexp.index('}}')
        except:
            break
        if end < start:
            break
        regexp = regexp[:start] + '(.*)' + regexp[end+2:]
    return re.compile(regexp)
