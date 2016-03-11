# -*- coding: utf-8 -*-
import json
from django.core.context_processors import csrf
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.views.generic import CreateView,TemplateView, ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from principal.models import DatosPersonales, PaginasWeb, Perfil, ListaPerfiles
from django.core import serializers
from array import *
from oauth_provider.decorators import oauth_required
from oauth_provider.models import Token
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from principal.operadorPermisos import OperadorPermisos

#No hace falta poner @oauth_required, @api_view ya lo hace si esta definido en Settings

#Devuelve los permisos de un usuario
#Formato de devolucion {"permisos": "0100000000000000"}
@api_view(['GET'])
def permisos(request):
    datos=DatosPersonales.objects.get(usuario=request.user)
    content={'permisos':datos.permisos}
    return Response(content)

#Devuelve los permisos de un usuario por palabras
@api_view(['GET'])
def permisosPorPalabras(request):
    datos=DatosPersonales.objects.get(usuario=request.user)
    op=OperadorPermisos(datos.permisos)
    content=op.elementosDisponibles()
    return Response(content)


#Almacena los permisos en DatosPersonales del usuario solicitante
#Parametro de entrada {"permisos": "0100000000000000"}
@api_view(['POST'])
def modificarPermisos(request):
    datos=DatosPersonales.objects.get(usuario=request.user)
    flag=False
    try :
        permisos=request.POST['permisos']
        for i in permisos:
            if i!='0' and i!='1':
                flag=True
        if flag!=True:
            datos.setPermisos(permisos)
            datos.save()
            content={'permisos':datos.permisos}
        else:
            content={'Error':'Formato incorrecto'}
    except MultiValueDictKeyError :
        content={'Error':'Formato incorrecto'}
    return Response(content)


#Almacena los permisos en DatosPersonales del usuario solicitante, pero estos permisos son recibidos por palabras y no por codigo
#Parametro de entrada {"permisos": ["apellidos", "nombre", "webPersonal", "webProfesional", "dni"]}
@api_view(['POST'])
def modificarPermisosPorPalabras(request):
    datos=DatosPersonales.objects.get(usuario=request.user)
    content={}
    op=OperadorPermisos('000000000000000000')
    try:
        permisos=op.setPermisosFromPalabras(request.DATA['permisos'])
        datos.setPermisos(permisos)
        datos.save()
        content=op.elementosDisponibles()
    except KeyError :
        content={'Error':'Formato incorrecto'}
    return Response(content)


#Elimina un perfil existente de la lista de perfiles del usuario solicitante
#Parametro de entrada Ej.{"codigo":"12345"}
@api_view(['POST'])
def cancelarPerfil(request):
    usuario=request.user
    lista=ListaPerfiles.objects.get(usuario=usuario)
    try:
        codigo=request.POST['codigo']
        try:
            perfil=Perfil.objects.get(codigo=codigo)
            if lista.eliminarPerfil(perfil):
                content={'Exito':'Perfil cancelado'}
            else:
                content={'Error':'No se posee el perfil suministrado'}
        except ObjectDoesNotExist:
            content={'Error':'No existe un perfil con ese codigo'}
    except KeyError:
        content={'Error':'Formato incorrecto'}
    return Response(content)

#Anade un perfil existente a la lista de perfiles del usuario solicitante
#Parametro de entrada Ej.{"codigo":"12345"}
@api_view(['POST'])
def nuevoPerfil(request):
    usuario=request.user
    try:
        codigo=request.POST['codigo']
        try:
             perfil=Perfil.objects.get(codigo=codigo)
             lista=ListaPerfiles.objects.get(usuario=usuario)
             lista.addPerfil(perfil)
             lista.save()
             content={'codigo':perfil.codigo}
        except ObjectDoesNotExist:
            content={'Error':'No existe un perfil con ese codigo'}
    except KeyError:
        content={'Error':'Formato incorrecto'}
    return Response(content)


#Devuelve todos los datos del usuario solicitante
@api_view(['GET'])
def user(request):
    usuario = request.user
    try:
        datos=DatosPersonales.objects.get(usuario=usuario)
        paginas=PaginasWeb.objects.get(usuario=usuario)
        info=OperadorPermisos('11111111111111111')
        content=info.getContent(usuario,datos,paginas)
    except ObjectDoesNotExist:
        content={'Error':'El usuario no existe o esta desactivo'}
    return Response(content)

#Devuelve la informacion de otro usuario
#Parametro de entrada Ej.{"username":"edu"}
@api_view(['GET'])
def other(request):
    usuario=request.user
    flag=True
    noHayAcuerdo=False
    permisos="000000000000000000"
    if usuario.is_active==True :
        #Buscamos si hay un perfil acordado
        try:
            usuarioTarget=User.objects.get(username=request.GET['username'])
            perfil=Perfil.objects.get(usuario=usuario)
            listaTarget=ListaPerfiles.objects.get(usuario=usuarioTarget)
            if listaTarget.hasPerfil(codigo=perfil.codigo):
                permisos=perfil.permisos #Si han acordado un perfil, se usan esos permisos
                flag=True
            else :
                noHayAcuerdo=True
        except ObjectDoesNotExist:
            flag=False

        try:
            if flag==False :
                usuarioTarget=User.objects.get(username=request.GET['username'])
            datosTarget = DatosPersonales.objects.get(usuario=usuarioTarget)
            paginasTarget=PaginasWeb.objects.get(usuario=usuarioTarget)
            if flag==False or noHayAcuerdo==True:
                permisos=datosTarget.permisos #Si no se ha acordado un perfil se usan los permisos del usuarioTarget
            operador =OperadorPermisos(permisos)
            content=operador.getContent(usuarioTarget, datosTarget, paginasTarget)
            usuarioTarget.clean()
        except ObjectDoesNotExist:
            content={'Error':'No existe usuario'}
    else:
        content={'Error':'No existe usuario'}
    return Response(content)

#Devuelve la informacion de un perfil dado un codigo
#Parametro de entrada Ej.{"codigo":"12345"}
#Parametro de salida Ej.{"usuario":"edu","permisos":"0111111111111111","descripcion":"Identificacion necesaria para azafatos"}
@api_view(['GET'])
def perfil(request):
    codigo=request.GET['codigo']
    try: #Try por si el codigo no existe
        perfil_usuario= Perfil.objects.get(codigo=codigo)
        lista_usuario=ListaPerfiles.objects.get(usuario=request.user)
        permisos=OperadorPermisos(perfil_usuario.permisos)
        if perfil_usuario in lista_usuario.perfiles.all() :
            content = {'usuario':perfil_usuario.usuario.username ,'permisos':permisos.permisosToList(), 'descripcion':perfil_usuario.descripcion, 'agregado':'True'}
        else:
            content = {'usuario':perfil_usuario.usuario.username ,'permisos':permisos.permisosToList(), 'descripcion':perfil_usuario.descripcion, 'agregado':'False'}
    except ObjectDoesNotExist:
        content ={'Error':'Codigo de perfil invalido'}

    return Response(content)

#Devuelve una lista de usarios y codigo de perfiles del usuario solicitante
#Parametro de salida Ej.{"0": ["edu", "1234"], "1": ["pepe", "12345"]}
@api_view(['GET'])
def listaPerfil(request):
    usuario=request.user
    lista_usuario=ListaPerfiles.objects.get(usuario=usuario)
    dict={}
    num=0
    for perfil in lista_usuario.perfiles.all():
        par=(perfil.usuario.username,perfil.codigo)
        dict.setdefault(num,par)
        num+=1
    return Response(dict)

@api_view(['GET'])
def check(request):
    content = {'Exito': 'Sus tokens siguen activos'}
    return Response(content)
