# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import ModelForm, Textarea, TextInput
from django import forms
from principal.models import DatosPersonales, PaginasWeb, Perfil, Imagen
from oauth_provider.models import Consumer
from django.contrib.auth.models import User
from array import *
from principal.operadorPermisos import OperadorPermisos
from principal.vuforiaHandler import VuforiaHandler
from captcha.fields import CaptchaField
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
import uuid

import urlparse
import oauth2 as oauth
import requests
import datetime
import os
import hashlib
import hmac
import base64
import json
FIELD_NAME_MAPPING = {
    'name': 'nombre',
    'description': 'descripcion'
}

class ImagenForm(ModelForm):
    class Meta:
        model=Imagen
        fields =['imagen']

    def enviar(self,name):
        diccionario_limpio = self.cleaned_data
        imagen=diccionario_limpio.get('imagen')
        conexion=VuforiaHandler()
        response=conexion.subirImagen(name=name,imagen=imagen)
        print response.content #JSON
        jsonResultado=json.loads(response.content)
        if jsonResultado.has_key('target_id'):
            target_id=jsonResultado['target_id']
            return target_id
        else:
            return "Error"

    def save(self,target,usuario,commit=True):
        instance = super(ImagenForm, self).save(commit=False)
        if commit:
            instance.usuario=usuario
            instance.target_id=target
            instance.save()


class nuevoUserForm(ModelForm):
    password1 = forms.CharField(max_length=10,widget=forms.PasswordInput(), required=True)
    password2 = forms.CharField(max_length=10,widget=forms.PasswordInput(), required=True)
    captcha = CaptchaField()
    class Meta:
        model=User
        fields =['username','email']

    def __init__(self, *args, **kwargs):
        super(nuevoUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text=_("30 caracteres o menos. Solo letras, números y @/./+/-/_")
        self.fields['password1'].label = _("Contraseña (Al menos 6 caracteres)")
        self.fields['password2'].label = _("Repita contraseña")
    	self.fields['captcha'].label=_("Introduzca lo siguiente")

    def clean_password2(self):
        diccionario_limpio = self.cleaned_data
        pass1=diccionario_limpio.get('password1')
        pass2=diccionario_limpio.get('password2')
        if pass1 != pass2:
            raise forms.ValidationError(_("Las contrasenas no son iguales."))
        return pass2

    def clean_password1(self):
        diccionario_limpio = self.cleaned_data
        pass1=diccionario_limpio.get('password1')
        if len(pass1)<6:
            raise forms.ValidationError(_("La contraseña tiene que tener al menos 6 caracteres."))
        return pass1

    def save(self, commit=True):
        user= super(nuevoUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserForm(ModelForm):
    class Meta:
        model=User
        fields = ['first_name','last_name', 'email']
        widgets = {
            'email': TextInput(attrs={}),
        }


class DatosPersonalesForm(ModelForm):
    class Meta:
        model = DatosPersonales
        fields =['dni','estatus','profesion','pais','empresa','telefono','direccion','comentario','nacimiento']
    def __init__(self, *args, **kwargs):
        super(DatosPersonalesForm, self).__init__(*args, **kwargs)
        self.fields['dni'].label= _("DNI")
        self.fields['estatus'].label=_("Estatus")
        self.fields['empresa'].label=_("Empresa")
        self.fields['comentario'].label=_("Comentario")
        self.fields['profesion'].label = _("Profesión")
        self.fields['pais'].label = _("País")
        self.fields['telefono'].label = _("Teléfono")
        self.fields['direccion'].label = _("Dirección")
        self.fields['nacimiento'].label=_("Fecha de nacimiento")

class PaginasWebForm(ModelForm):
    class Meta:
        model = PaginasWeb
        fields = ['facebook', 'twitter', 'linkedin', 'webPersonal', 'webProfesional']
        #Danjgo 1.6 convierte el type en url, pero me parece mas interesante que el texto sea type=text
        widgets = {
            'facebook': TextInput(attrs={}),
            'twitter': TextInput(attrs={}),
            'linkedin': TextInput(attrs={}),
            'webPersonal': TextInput(attrs={}),
            'webProfesional': TextInput(attrs={}),
        }
    def __init__(self, *args, **kwargs):
        super(PaginasWebForm, self).__init__(*args, **kwargs)
        self.fields['webPersonal'].label = _("Web Personal")
        self.fields['webProfesional'].label = _("Web Profesional")

#widget=forms.CheckboxInput(attrs={'value': 'ó'})
class PerfilForm(ModelForm):
    apellidos = forms.BooleanField(initial=False, required=False, label=_("Apellidos"))
    comentario =forms.BooleanField(initial=False, required=False, label=_("Comentario"))
    direccion=forms.BooleanField(initial=False, required=False, label=_("Dirección"))
    dni=forms.BooleanField(initial=False, required=False, label=_("DNI"))
    email=forms.BooleanField(initial=False, required=False, label=_("Email"))
    empresa=forms.BooleanField(initial=False, required=False, label=_("Empresa"))
    estatus=forms.BooleanField(initial=False, required=False, label=_("Estatus"))
    facebook=forms.BooleanField(initial=False, required=False)
    linkedin=forms.BooleanField(initial=False, required=False)
    nombre=forms.BooleanField(initial=False, required=False, label=_("Nombre"))
    nacimiento=forms.BooleanField(initial=False,required=False, label=_("Fecha de nacimiento"))
    pais=forms.BooleanField(initial=False, required=False, label=_("País"))
    profesion=forms.BooleanField(initial=False, required=False, label=_("Profesión"))
    telefono=forms.BooleanField(initial=False, required=False, label = _("Teléfono"))
    twitter=forms.BooleanField(initial=False, required=False)
    webPersonal=forms.BooleanField(initial=False, required=False, label = _("Web personal"))
    webProfesional=forms.BooleanField(initial=False, required=False, label = _("Web profesional"))
    class Meta:
        model = Perfil
        fields =['descripcion']

    def __init__(self, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        self.fields['descripcion'].label = _("Descripción")

    def save(self, commit=True):
        instance = super(PerfilForm, self).save(commit=False)
        operator=OperadorPermisos(stringPermisos='')
        instance.permisos= operator.conversor(self.cleaned_data)
        if commit:
            instance.generarCodigo()
        return instance


class ConsumerForm(ModelForm):
    class Meta:
        model =Consumer
        fields =['name','description']
    def __init__(self, *args, **kwargs):
        super(ConsumerForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = _("Nombre de la aplicación :")
        self.fields['description'].label = _("Descripción :")

    def clean_name(self):
        diccionario_limpio = self.cleaned_data
        name=diccionario_limpio.get('name')
        if Consumer.objects.filter(name=name).exists():
            raise forms.ValidationError(_("Ya existe una aplicación con ese nombre."))
        return name

    def save(self, commit=True):
        instance = super(ConsumerForm, self).save(commit=False)
        if commit:
             instance.status=2
             instance.generate_random_codes()
        return instance

