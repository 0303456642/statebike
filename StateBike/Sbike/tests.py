# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from Sbike import views
import os

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
        'weblogin' : 'web_login.html'
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
        self.assertNotEqual(-1, res.content.index('You Have Successfully Registered'))


    def test_login(self):
        """ Intentamos loguearnos (in)validamente """

        # Nos intentamos loguear con un usuario inexistente
        c = Client()
        self.assertFalse(c.login(username='probablementeningunusuarioexistaconestenombre', password='miranda'))

        # ahora nos registramos 
        res = c.post('/register/', self.formValid, follow = True)        

        # deberiamos obtener el login
        self.assertTrue(self.is_template(res, self.templates['weblogin']))

        # y recibir el msj de exito
        self.assertNotEqual(-1, res.content.index('You Have Successfully Registered'))

        # y ahora intentamos loguearnos
        self.assertTrue(c.login(username=self.formValid['username'], password=self.formValid['password1']))


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

    def is_template(self, res, filename):
        titles_match = self.titles_match(res, filename)

        return titles_match

    def titles_match(self, res, templ):
        bar_title = self.get_content_title(res.content) == self.get_template_title(templ)

        h1_title = self.get_content_h1(res.content) == self.get_template_h1(templ)

        # print('bar content: "'+ str(self.get_content_title(res.content)) +'"')
        # print('bar template: "'+str(self.get_template_title(templ))+'"')

        # print('h1 content: "'+ str(self.get_content_h1(res.content)) +'"')
        # print('h1 template: "'+str(self.get_template_h1(templ))+'"')

        return bar_title and h1_title


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


