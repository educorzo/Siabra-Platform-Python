# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib.auth.models import User

from principal.models import DatosPersonales, PaginasWeb, Perfil, ListaPerfiles
from django.template import Template, Context
from django.utils.unittest import TestCase
from rest_framework.test import APIClient
import json



class TestRestGet(TestCase):
    cliente = APIClient()
    vacioJson={'apellidos': '','comentario': '','direccion': '','dni': '','email': '','empresa': '','estatus': '','facebook': '','linkedin': '','nacimiento': '','nombre': '','pais': '','profesion': '','telefono': '','twitter': '','webPersonal': '','webProfesional': ''}

    todoPepeJson={'apellidos': 'Peña','comentario': u'Hola !','direccion': 'los metales','dni': u'72233345B','email': 'pepepena@gmail.com','empresa': u'Sigma','estatus': 'casado','facebook': u'www.facebook.com/pepePena','linkedin': 'www.linkedin.com/josePena','nacimiento':'1920-10-18','nombre': u'Jose','pais': 'España','profesion': u'vendedor','telefono': '0034958153120','twitter': u'www.twitter.com/pepePena','webPersonal': 'www.pepe.wordpress.com','webProfesional': 'http://www.sigma.es'}

    publicoPepeJson={'profesion': '', 'empresa': u'Sigma', 'webPersonal': u'www.pepe.wordpress.com', 'estatus': '', 'twitter': '', 'dni': u'72233345B', 'linkedin': '', 'comentario': u'Hola !', 'apellidos': '', 'facebook': u'www.facebook.com/pepePena', 'pais': u'España', 'nombre': '', 'nacimiento': '1920-10-18', 'direccion': '', 'telefono': u'0034958153120', 'email': '', 'webProfesional': ''}

    todoLolaJson={'apellidos': u'Molina','comentario': u'','direccion': u'los metales','dni': u'78888889B','email': u'artista@gmail.com','empresa': u'','estatus': u'casado','facebook': u'www.facebook.com/lolaMolina','linkedin': u'www.linkedin.com/lolaMolina','nacimiento': u'1920-10-18','nombre': u'Dolores','pais': u'Espa\xf1a', 'profesion': u'ama de casa','telefono': u'0034958153120','twitter': u'www.twitter.com/lolaMolina','webPersonal': u'www.lola.wordpress.com','webProfesional': u''}

    def setUp(self):
        #USUARIO PEPE
        User.objects.create(username='pepe', first_name='Jose', last_name='Peña', email='pepepena@gmail.com')
        user=User.objects.get(username='pepe')
        DatosPersonales.objects.create(usuario=user,dni='72233345B',nacimiento='1920-10-18',profesion='vendedor',estatus='casado',pais='España',empresa='Sigma',telefono='0034958153120',permisos='01010101010101010', direccion='los metales', comentario='Hola !')
        PaginasWeb.objects.create(usuario=user,facebook='www.facebook.com/pepePena', twitter='www.twitter.com/pepePena',linkedin='www.linkedin.com/josePena', webPersonal='www.pepe.wordpress.com',webProfesional='http://www.sigma.es')
        perfil=Perfil.objects.create(usuario=user,codigo='1234',permisos='11111111111111111', descripcion='Un perfil para hacer pruebas de todo tipo. ñ')

        ListaPerfiles.objects.create(usuario=user)
        #USUARIO LOLA
        User.objects.create(username='lola', first_name='Dolores',last_name='Molina',email='artista@gmail.com')
        user2=User.objects.get(username='lola')
        DatosPersonales.objects.create(usuario=user2,dni='78888889B',nacimiento='1920-10-18',profesion='ama de casa',estatus='casado',pais='España',empresa='',telefono='0034958153120',permisos='00000000000000000', direccion='los metales')
        PaginasWeb.objects.create(usuario=user2,facebook='www.facebook.com/lolaMolina', twitter='www.twitter.com/lolaMolina',linkedin='www.linkedin.com/lolaMolina', webPersonal='www.lola.wordpress.com',webProfesional='')
        listaperfiles2=ListaPerfiles.objects.create(usuario=user2)
        listaperfiles2.perfiles.add(perfil)
        #USUARIO ANONIMO
        User.objects.create(username='anonimo')
        #USUARIO NO ACTIVO
        User.objects.create(username='loli', first_name='mercedez', is_active=False)

    def tearDown(self):
        User.objects.all().delete()
        DatosPersonales.objects.all().delete()
        PaginasWeb.objects.all().delete()
        Perfil.objects.all().delete()
        ListaPerfiles.objects.all().delete()


    #principal.rest.permisos
    def test_show_permisos_code(self):
       user=User.objects.get(username='pepe')
       self.cliente.force_authenticate(user=user)
       response = self.cliente.get('/permisos/show/code/')
       self.assertEqual(response.data, {"permisos": "01010101010101010"})

    #principal.rest.permisosPorPalabras
    def test_show_permisos_words(self):
       user=User.objects.get(username='pepe')
       self.cliente.force_authenticate(user=user)
       response =self.cliente.get('/permisos/show/words/')
       self.assertEqual(response.data, {'permisos': ['comentario', 'dni', 'empresa', 'facebook', 'nacimiento', 'pais', 'telefono', 'webPersonal']})

    #principal.rest.user
    def test_show_datos_propio_usuario(self):
        user=User.objects.get(username='pepe')
        self.cliente.force_authenticate(user=user)
        response = self.cliente.get('/user/show/')
        self.assertEqual(response.data,self.todoPepeJson)

    def test_consulta_usuario_no_activo(self):
        user=User.objects.get(username='loli')
        self.cliente.force_authenticate(user=user)
        response = self.cliente.get('/user/show/')
        self.assertEqual(response.data,{'Error': 'El usuario no existe o esta desactivo'})

    #principal.rest.other
    def test_show_datos_otro_usuario_usando_perfil(self):
        pepe=User.objects.get(username='pepe')
        self.cliente.force_authenticate(user=pepe)
        response= self.cliente.get('/user/other/',{'username':'lola'})
        self.assertEqual(response.data, self.todoLolaJson)

    def test_show_datos_otro_usuario_asimismo_con_perfil_no_aceptado_restrictivo(self):
        pepe=User.objects.get(username='pepe')
        self.cliente.force_authenticate(user=pepe)
        response= self.cliente.get('/user/other/',{'username':'pepe'})
        self.assertEqual(response.data, self.publicoPepeJson)


    def test_show_datos_otro_usuario(self):
        anonimo=User.objects.get(username='anonimo')
        self.cliente.force_authenticate(user=anonimo)
        response= self.cliente.get('/user/other/',{'username':'pepe'})
        self.assertEqual(response.data,self.publicoPepeJson)


    def test_show_datos_otro_usuario_con_todo_privado(self):
        anonimo=User.objects.get(username='anonimo')
        self.cliente.force_authenticate(user=anonimo)
        response= self.cliente.get('/user/other/',{'username':'lola'})
        self.assertEqual(response.data,self.vacioJson)

    def test_show_datos_otro_usuario_que_no_existe(self):
        anonimo=User.objects.get(username='anonimo')
        self.cliente.force_authenticate(user=anonimo)
        response= self.cliente.get('/user/other/',{'username':'eduardo'})
        self.assertEqual(response.data,{'Error': 'No existe usuario'})

    def test_show_datos_otro_usuario_que_no_esta_activo(self):
        anonimo=User.objects.get(username='anonimo')
        self.cliente.force_authenticate(user=anonimo)
        response= self.cliente.get('/user/other/',{'username':'loli'})
        self.assertEqual(response.data,{'Error': 'No existe usuario'})


    #principal.rest.perfil
    def test_show_perfil_existente(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.get('/perfil/show/',{'codigo':'1234'})
        self.assertEqual(response.data,{'agregado': 'True', 'descripcion': u'Un perfil para hacer pruebas de todo tipo. ñ','permisos': ['apellidos', 'comentario', 'direccion', 'dni', 'email', 'empresa', 'estatus', 'facebook', 'linkedin', 'nacimiento', 'nombre', 'pais', 'profesion', 'telefono', 'twitter', 'webPersonal', 'webProfesional'],'usuario': u'pepe'})

    def test_show_perfil_inexistente(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.get('/perfil/show/',{'codigo':'12'})
        self.assertEqual(response.data,{'Error':'Codigo de perfil invalido'})

    #principal.rest.listaPerfil
    def test_show_lista_perfiles_con_perfiles(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.get('/perfil/list/')
        self.assertEqual(response.data,{0: (u'pepe', u'1234')})

    def test_show_lista_perfiles_vacio(self):
        pepe=User.objects.get(username='pepe')
        self.cliente.force_authenticate(user=pepe)
        response= self.cliente.get('/perfil/list/')
        self.assertEqual(response.data,{})


class TestRestPost(TestCase):
    cliente = APIClient()
    def setUp(self):
        #USUARIO PEPE
        User.objects.create(username='pepe', first_name='Jose', last_name='Peña', email='pepepena@gmail.com')
        user=User.objects.get(username='pepe')
        DatosPersonales.objects.create(usuario=user,dni='72233345B',nacimiento='1920-10-18',profesion='vendedor',estatus='casado',pais='España',empresa='Sigma',telefono='0034958153120',permisos='01010101010101010', direccion='los metales', comentario='Hola !')
        PaginasWeb.objects.create(usuario=user,facebook='www.facebook.com/pepePena', twitter='www.twitter.com/pepePena',linkedin='www.linkedin.com/josePena', webPersonal='www.pepe.wordpress.com',webProfesional='http://www.sigma.es')
        perfil=Perfil.objects.create(usuario=user,codigo='1234',permisos='11111111111111111', descripcion='Un perfil para hacer pruebas de todo tipo. ñ')
        ListaPerfiles.objects.create(usuario=user)
        #USUARIO LOLA
        User.objects.create(username='lola', first_name='Dolores',last_name='Molina',email='artista@gmail.com')
        user2=User.objects.get(username='lola')
        DatosPersonales.objects.create(usuario=user2,dni='78888889B',nacimiento='1920-10-18',profesion='ama de casa',estatus='casado',pais='España',empresa='',telefono='0034958153120',permisos='00000000000000000', direccion='los metales')
        PaginasWeb.objects.create(usuario=user2,facebook='www.facebook.com/lolaMolina', twitter='www.twitter.com/lolaMolina',linkedin='www.linkedin.com/lolaMolina', webPersonal='www.lola.wordpress.com',webProfesional='')
        listaperfiles2=ListaPerfiles.objects.create(usuario=user2)
        listaperfiles2.perfiles.add(perfil)
        #USUARIO ANONIMO
        user3=User.objects.create(username='anonimo')
        ListaPerfiles.objects.create(usuario=user3)

    def tearDown(self):
        User.objects.all().delete()
        DatosPersonales.objects.all().delete()
        PaginasWeb.objects.all().delete()
        Perfil.objects.all().delete()
        ListaPerfiles.objects.all().delete()

    #principal.rest.modificarPermisos
    def test_modificar_permisos_por_codigo(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/permisos/modify/code/',{"permisos": "11111111111111111"})
        self.assertEqual(response.data,{"permisos": "11111111111111111"})

    def test_modificar_permisos_por_codigo_con_nombre_erroneo(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/permisos/modify/code/',{"per": "11111111111111111"})
        self.assertEqual(response.data,{'Error': 'Formato incorrecto'})

    def test_modificar_permisos_por_codigo_con_parametro_erroneo(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/permisos/modify/code/',{"per": "1a111111111111111"})
        self.assertEqual(response.data,{'Error': 'Formato incorrecto'})

    #principal.rest.modificarPermisosPorPalabras
    def test_modificar_permisos_por_palabras(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/permisos/modify/words/',json.dumps({"permisos": ["apellidos", "nombre", "webPersonal", "webProfesional", "dni"]}),content_type='application/json')
        self.assertEqual(response.data,{"permisos": ["apellidos","dni", "nombre", "webPersonal", "webProfesional"]})

    def test_modificar_permisos_por_palabras_con_parametro_erroneo(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/permisos/modify/words/',json.dumps({"fallo": ["apellidos", "nombre", "webPersonal", "webProfesional", "dni"]}),content_type='application/json')
        self.assertEqual(response.data,{'Error':'Formato incorrecto'})

    def test_modificar_permisos_por_palabras_vacio(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/permisos/modify/words/',json.dumps({"permisos": []}),content_type='application/json')
        self.assertEqual(response.data,{"permisos": []})

    def test_modificar_permisos_por_palabra_incorrecta(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/permisos/modify/words/',json.dumps({"permisos": ["nada"]}),content_type='application/json')
        self.assertEqual(response.data,{"permisos": []})

    #principal.rest.cancelarPerfil
    def test_cancelar_perfil(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/perfil/cancel/',{"codigo": "1234"})
        self.assertEqual(response.data,{'Exito':'Perfil cancelado'})

    def test_cancelar_perfil_no_existente(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/perfil/cancel/',{"codigo": "111"})
        self.assertEqual(response.data,{'Error':'No existe un perfil con ese codigo'})

    def test_cancelar_perfil_con_parametro_erroneo(self):
        lola=User.objects.get(username='lola')
        self.cliente.force_authenticate(user=lola)
        response= self.cliente.post('/perfil/cancel/',{"code": "111"})
        self.assertEqual(response.data,{'Error':'Formato incorrecto'})

    #principal.rest.nuevoPerfil
    def test_nuevo_perfil(self):
        anonimo=User.objects.get(username='anonimo')
        self.cliente.force_authenticate(user=anonimo)
        response= self.cliente.post('/perfil/new/',{"codigo": "1234"})
        self.assertEqual(response.data,{"codigo":"1234"})

    def test_nuevo_perfil_inexistente(self):
        anonimo=User.objects.get(username='anonimo')
        self.cliente.force_authenticate(user=anonimo)
        response= self.cliente.post('/perfil/new/',{"codigo": "111"})
        self.assertEqual(response.data,{'Error':'No existe un perfil con ese codigo'})

    def test_nuevo_perfil_con_parametro_erroneo(self):
        anonimo=User.objects.get(username='anonimo')
        self.cliente.force_authenticate(user=anonimo)
        response= self.cliente.post('/perfil/new/',{"code": "111"})
        self.assertEqual(response.data,{'Error':'Formato incorrecto'})














