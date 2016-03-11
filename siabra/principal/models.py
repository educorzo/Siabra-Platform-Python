#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

import uuid
import os
# Create your models here.

class DatosPersonales(models.Model):
        usuario =models.ForeignKey(User, primary_key=True)
        dni = models.CharField(max_length=9, blank= True)
        profesion= models.CharField(max_length=20, blank=True)
        estatus=models.CharField(max_length=20, blank=True,  help_text=_('Ej. Soltero.'))
        pais=models.CharField(max_length=20, blank=True )
        empresa=models.CharField(max_length=20,blank=True)
        comentario=models.CharField(max_length=50,blank=True, help_text=_('Ej. Hola! Estoy usando SIABRA.'))
        telefono=models.CharField(max_length=13,blank=True)
        direccion=models.CharField(max_length=50, blank=True)
        nacimiento= models.DateField(auto_now=False, null=True, blank=True, help_text=_('Ej. dd/mm/aaaa'))
        permisos=models.CharField(max_length=17,default='00000000000000000')
        def __unicode__(self):
            return unicode(self.usuario)

        def setPermisos(self, permisos):
            self.permisos=permisos[:17]

class PaginasWeb(models.Model):
        usuario =models.ForeignKey(User,primary_key=True)
        facebook = models.URLField(max_length=90, blank=True, help_text=_('Ej. www.facebook.com/NombreApellido'))
        twitter = models.URLField(max_length=90, blank=True, help_text=_('Ej. www.twitter.com/Usuario'))
        linkedin = models.URLField(max_length=90, blank=True, help_text=_('Ej. es.linkedin.com/in/eduardocorzo/'))
        webPersonal = models.URLField(max_length=90, blank=True, help_text=_('Ej. www.pepe.wordpress.com'))
        webProfesional = models.URLField(max_length=90, blank=True, help_text=_('Ej. http://biosearchlife.com'))

        def __unicode__(self):
                return unicode(self.usuario)

class Perfil(models.Model):
        usuario =models.ForeignKey(User, unique=True)
        codigo =models.CharField(max_length=10, primary_key=True)
        permisos=models.CharField(max_length=17)
        descripcion=models.TextField(max_length=200, blank=True)

        #Genera un codigo y lo salva. Sustituir funcion por Save()
        def generarCodigo(self):
            prueba=uuid.uuid4().hex
            self.codigo=prueba[:10]
            self.save()

        def __str__(self):
            return '%s %s' % (self.codigo, self.usuario.username)

class ListaPerfiles(models.Model):
        usuario =models.ForeignKey(User,primary_key=True)
        perfiles=models.ManyToManyField(Perfil)

        def __unicode__(self):
                return unicode(self.usuario)

        def hasPerfil(self,codigo):
            #if self.perfiles.filter(codigo=codigo).count() ==1 :
            if self.perfiles.filter(codigo=codigo).exists():
                return True
            else:
                return False

        def addPerfil(self, perfil):
            self.perfiles.add(perfil)

        def eliminarPerfil(self, perfil):
            if perfil in self.perfiles.all() :
                self.perfiles.remove(perfil)
                return True
            else:
                return False

class Imagen(models.Model):
        usuario =models.ForeignKey(User,primary_key=True)
        imagen=models.ImageField(upload_to='imagenes')
        target_id=models.CharField(max_length=32, blank=True)
        def __unicode__(self):
            return unicode(self.usuario)

        def rename(self,name):
            old_name= self.imagen.name
            self.imagen.name="imagenes/"+name+".jpg"
            #archivoOrigen=os.getcwd()+"/media/imagenes/"+old_name
            archivoOrigen=os.getcwd()+"/media/"+old_name
            archivoResultado=os.getcwd()+"/media/imagenes/"+name+".jpg"
            print "oldName "+old_name
            print "construido "+self.imagen.name
            print "inicio "+archivoOrigen
            print "fin "+archivoResultado
            os.rename(archivoOrigen, archivoResultado)

        #def save(self, *args, **kwargs):
         #   self.rename(self.target_id)
         #   super(Imagen, self).save(*args, **kwargs)