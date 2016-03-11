# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.forms import UserCreationForm
from django.core.context_processors import csrf
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,redirect
from django.template import Template, Context
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.views.generic import CreateView,TemplateView, ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from oauth_provider.models import Nonce, Token, Consumer, Scope, VERIFIER_SIZE
from oauth_provider.store import Store
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from principal.forms import DatosPersonalesForm, PaginasWebForm, PerfilForm, UserForm, ConsumerForm, nuevoUserForm, ImagenForm
from principal.models import DatosPersonales, PaginasWeb, Perfil, Imagen, ListaPerfiles
from django.core.exceptions import ObjectDoesNotExist
from principal.operadorPermisos import OperadorPermisos
from principal.vuforiaHandler import VuforiaHandler
from django.utils.translation import ugettext as _
import os

def welcome(request, parametro=None):
    if request.user.is_authenticated():
		return HttpResponseRedirect('home')
    dict={}
    if parametro=='1':
        dict.setdefault('eliminado',True)
    #Formulario registrar
    if request.method=='POST' and 'Registrar' in request.POST:
        formularioRegister=nuevoUserForm(request.POST)
        if formularioRegister.is_valid():
            formularioRegister.save()
            acceso = authenticate(username=request.POST["username"], password=request.POST["password1"])
            login(request, acceso)
            usuario=User.objects.get(username=request.POST["username"])
            crearObjetos(usuario)
            return redirect('home')
        else:
            dict={}
            dict.setdefault('eliminado',False)
    else:
		formularioRegister=nuevoUserForm()

    #Formulario Login
    if request.method=='POST' and 'Login' in request.POST:
        usuario = request.POST['username']
        clave = request.POST['password']
        acceso = authenticate(username=usuario, password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return redirect('home')
            else:
                dict={}
                dict.setdefault('error',_('El usuario no esta activo'))
                dict.setdefault('eliminado',False)
        else:
            dict={}
            dict.setdefault('error',_('Contraseña o usuario incorrecto'))
            dict.setdefault('eliminado',False)
    dict.setdefault('formularioRegister',formularioRegister)
    return render_to_response('welcome.html',dict, context_instance=RequestContext(request))

def crearObjetos(usuario):
    datos=DatosPersonales()
    datos.usuario=usuario
    datos.save()
    paginas=PaginasWeb()
    paginas.usuario=usuario
    paginas.save()

@login_required(login_url='welcome')
def add_imagen(request):
    dict={}
    try:
        imagen = Imagen.objects.get(usuario=request.user)
        dict.setdefault('creado',True)
        dict.setdefault('imagen',imagen.imagen)
    except ObjectDoesNotExist:
        dict.setdefault('creado',False)
        imagen=Imagen(usuario=request.user)
        if request.method=='POST' :
            print 'POSTNAME '+request.user.username
            formulario =ImagenForm(request.POST, request.FILES)
            dict.setdefault('formulario',formulario)
            if formulario.is_valid():
                target_id=formulario.enviar(name=request.user.username)
             #   target_id="1111prueba"
                if target_id!="Error":
                    formulario.save(target=target_id, usuario=request.user)
                    imagen=Imagen.objects.get(usuario=request.user)
                    print imagen.target_id
                    imagen.rename(name=target_id)
                    imagen.save()
                    return HttpResponseRedirect('')
                else:
                    dict.setdefault('Error',True)
        else:
            formulario = ImagenForm(request.POST, request.FILES)
            dict.setdefault('formulario',formulario)
    return render_to_response('subirImagenForm.html',dictionary=dict,context_instance=RequestContext(request))





@login_required(login_url='welcome')
def modificar_paginas_web(request):
    try:
        profile = PaginasWeb.objects.get(usuario=request.user)
    except ObjectDoesNotExist: #Si no existe crea uno nuevo
        profile=PaginasWeb()
        profile.usuario=request.user
    if request.method=='POST':
        formulario = PaginasWebForm(request.POST or None, instance=profile)
        if formulario.is_valid():
            formulario.save()
            return render_to_response('paginasWebForm.html',{'formulario':formulario, 'exito':True}, context_instance=RequestContext(request))
    else:
        formulario = PaginasWebForm(instance=profile)
    return render_to_response('paginasWebForm.html',{'formulario':formulario}, context_instance=RequestContext(request))


@login_required(login_url='welcome')
def modificar_datos_personales(request):
    usuario=request.user
    try:
        datos = DatosPersonales.objects.get(usuario=usuario)
    except ObjectDoesNotExist: #Si no existe crea uno nuevo
        datos=DatosPersonales()
        datos.usuario=usuario
    if request.method=='POST' and 'Confirmar' in request.POST:
        user_form = UserForm(request.POST or None, instance=usuario)
        datos_form = DatosPersonalesForm(request.POST or None, instance=datos)
        if user_form.is_valid() and datos_form.is_valid():
            user_form.save()
            datos_form.save()
            return render_to_response('datosPersonalesForm.html',{'user_form':user_form, 'datos_form':datos_form, 'exito':True}, context_instance=RequestContext(request))
            #return HttpResponseRedirect('datos')
    else:
        user_form = UserForm(request.POST or None, instance=usuario)
        datos_form = DatosPersonalesForm(request.POST or None, instance=datos)

    if request.method=='POST' and 'eliminar' in request.POST:

        conexion=VuforiaHandler()
        try:
            imagen = Imagen.objects.get(usuario=usuario)
            response=conexion.eliminarImagen(target_id=imagen.target_id)
            print response.content #JSON
            Imagen.objects.filter(usuario=usuario).delete()
        except ObjectDoesNotExist:
            print "Error Object doesnt exist"
        usuario.is_active=False
        usuario.save()
        DatosPersonales.objects.filter(usuario=usuario).delete()
        PaginasWeb.objects.filter(usuario=usuario).delete()
        Perfil.objects.filter(usuario=usuario).delete()
        ListaPerfiles.objects.filter(usuario=usuario).delete()
        Token.objects.filter(user=usuario).delete()
        Consumer.objects.filter(user=usuario).delete()
        logout(request)
        return redirect('eliminado/1')

    return render_to_response('datosPersonalesForm.html',{'user_form':user_form, 'datos_form':datos_form}, context_instance=RequestContext(request))


@login_required(login_url='welcome')
def crear_aplicacion(request):
    dict={}
    if request.method=='POST' and 'eliminar' in request.POST:
        try:
            consumer = Consumer.objects.get(user=request.user)
            consumer.delete()
            dict.setdefault('creado',False)
            dict.setdefault('eliminado',True)
            #return HttpResponseRedirect('')
        except ObjectDoesNotExist:
            dict.setdefault('creado',False)
    try:
        consumer = Consumer.objects.get(user=request.user)
        dict.setdefault('creado',True)
        dict.setdefault('key',consumer.key)
        dict.setdefault('secret',consumer.secret)
        dict.setdefault('descripcion',consumer.description)
        dict.setdefault('nombre',consumer.name)
    except ObjectDoesNotExist:
        dict.setdefault('creado',False)
        consumer=Consumer(user=request.user)
        if request.method=='POST' and 'Confirmar' in request.POST:
            formulario =ConsumerForm(request.POST, instance=consumer)
            if formulario.is_valid():
                formulario.save()
                return HttpResponseRedirect('')
        else:
            formulario = ConsumerForm(instance=consumer)
            dict.setdefault('formulario',formulario)
    return render_to_response('aplicacionForm.html',dictionary=dict,context_instance=RequestContext(request))


#PAGINA PARA CREAR UN PERFIL
#SI EL PERFIL EXISTE MOSTRARA SU INFORMACION Y UN ENLANCE PARA ELIMINARLO
#SI EL PERFIL NO EXISTE MOSTRARA UN FORMULARIO A RELLENAR
@login_required(login_url='welcome')
def crear_perfil(request):
    dict={}
    if request.method=='POST' and 'eliminar' in request.POST:#Si existe el perfil se da la posibilidad de elimarlo
        try:
            perfil=Perfil.objects.get(usuario=request.user)
            print 'eliminado'
            perfil.delete()
            dict.setdefault('creado',False)
            dict.setdefault('eliminado',True)
        #return HttpResponseRedirect('')
        except ObjectDoesNotExist:
            dict.setdefault('creado',False)
    try:
        perfil = Perfil.objects.get(usuario=request.user)
        dict.setdefault('creado',True)
        dict.setdefault('descripcion',perfil.descripcion)
        dict.setdefault('codigo',perfil.codigo)
        operador=OperadorPermisos(perfil.permisos)
        dict.setdefault('permisos',operador.elementosDisponibles()['permisos'])
    except ObjectDoesNotExist:
        dict.setdefault('creado',False)
        perfil=Perfil(usuario=request.user)
        if request.method=='POST' and 'Confirmar' in request.POST:
            formulario = PerfilForm(request.POST, instance=perfil)
            if formulario.is_valid():
                formulario.save()
                return HttpResponseRedirect('')
        else:
            formulario = PerfilForm(instance=perfil)
            dict.setdefault('formulario',formulario)
    return render_to_response('perfilForm.html',dictionary=dict, context_instance=RequestContext(request))



#Permite autorizar una aplicacion, requiere login, si no existe login redirige a /accounts/login (loginAuthorize)
def oauth_authorize(request,info,callback,tokenrequest):
    token=tokenrequest[12:]
    nombreApp=info.consumer.name
    descripcionApp=info.consumer.description
    dic ={'token':token,'nombreApp':nombreApp, 'descripcion':descripcionApp}
    return render_to_response('authorizeApp.html',dic,context_instance=RequestContext(request))

def callback_view(request, **arg):
    token=Token.objects.get(key=arg.get("oauth_token"))
    dic={'verificador':token.verifier}
    return render_to_response('verificadorApp.html',dic,context_instance=RequestContext(request))

#Muestra una ventana de login especifica para autorizar aplicaciones
def loginAuthorize(request):
    dict={}
    next= request.GET['next'] #Si hay exito en el login nos volvera a llevar a Oauth authorize
    if request.method=='POST' and 'Login' in request.POST:
        usuario = request.POST['username']
        clave = request.POST['password']
        acceso = authenticate(username=usuario, password=clave)
        if acceso is not None:
            if acceso.is_active:
                login(request, acceso)
                return HttpResponseRedirect(next)
            else:
                dict.setdefault('error',_('El usuario no esta activo'));
        else:
            dict.setdefault('error',_('Usuario o contrasena incorrecto'))

    return render_to_response('login.html',dict, context_instance=RequestContext(request))




@login_required(login_url='welcome')
def home(request):
    return render_to_response('home.html',context_instance=RequestContext(request))

@login_required(login_url='welcome')
def acerca(request):
    return render_to_response('acerca.html',context_instance=RequestContext(request))

def acerca_no_logueado(request):
	dict={}
    #Formulario Login
	if request.method=='POST' and 'Login' in request.POST:
	    usuario = request.POST['username']
	    clave = request.POST['password']
	    acceso = authenticate(username=usuario, password=clave)
	    if acceso is not None:
	        if acceso.is_active:
	            login(request, acceso)
	            return render_to_response('home.html', context_instance=RequestContext(request))
	        else:
	            dict.setdefault('error',_('El usuario no esta activo'))
	    else:
	        dict.setdefault('error',_('Contraseña o usuario incorrecto'))
	return render_to_response('acercaNoLog.html',dict, context_instance=RequestContext(request))

@login_required(login_url='welcome')
def documentacion(request):
    return render_to_response('documentacion.html',context_instance=RequestContext(request))

def pagina_no_encontrada(request):
    return render_to_response('home.html',context_instance=RequestContext(request))


@login_required(login_url='welcome')
def cerrar(request):
    logout(request)
    return HttpResponseRedirect('/')
