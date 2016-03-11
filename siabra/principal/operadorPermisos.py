# -*- coding: utf-8 -*-
#encoding:utf-8
from principal.models import DatosPersonales, PaginasWeb, Perfil
from array import *
from django.contrib.auth.models import User

class OperadorPermisos():
        _permisos=array('c', ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'])
        _content ={}
        def setArrayPermisos(self, data):
            self._permisos=data
        def setDictionary(self, dict):
            self._content=dict
        def getArrayPermisos(self):
            return self._permisos
        def getPermisos(self):
            return ''.join(self._permisos)

        def setPermisosFromPalabras(self, data):
            self._permisos=array('c', ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0']) #TODOS LOS PERMISOS SE INICIALIZAN
            if 'apellidos' in data:
                self._permisos[0]='1'
            if 'comentario' in data:
                self._permisos[1]='1'
            if 'direccion' in data:
                self._permisos[2]='1'
            if 'dni' in data:
                self._permisos[3]='1'
            if 'email' in data:
                self._permisos[4]='1'
            if 'empresa' in data:
                self._permisos[5]='1'
            if 'estatus' in data:
                self._permisos[6]='1'
            if 'facebook' in data:
                self._permisos[7]='1'
            if 'linkedin' in data:
                self._permisos[8]='1'
            if 'nacimiento' in data:
                self._permisos[9]='1'
            if 'nombre' in data:
                self._permisos[10]='1'
            if 'pais' in data:
                self._permisos[11]='1'
            if 'profesion' in data:
                self._permisos[12]='1'
            if 'telefono' in data:
                self._permisos[13]='1'
            if 'twitter' in data:
                self._permisos[14]='1'
            if 'webPersonal' in data:
                self._permisos[15]='1'
            if 'webProfesional' in data:
                self._permisos[16]='1'
            return ''.join(self._permisos)


        #Devuelve un diccionario con sus respectivos valores de acuerdo con los permisos
        def getContent(self,User,DatosPersonales, PaginasWeb):
            self._content={}
            if self._permisos[0]=='1' :
                self._content.setdefault('apellidos', User.last_name)
            else:
                self._content.setdefault('apellidos', '')
            if self._permisos[1]=='1' :
                self._content.setdefault('comentario', DatosPersonales.comentario)
            else:
                self._content.setdefault('comentario', '')
            if self._permisos[2]=='1' :
                self._content.setdefault('direccion', DatosPersonales.direccion)
            else:
                self._content.setdefault('direccion', '')
            if self._permisos[3]=='1' :
                self._content.setdefault('dni',DatosPersonales.dni)
            else:
                self._content.setdefault('dni', '')
            if self._permisos[4]=='1' :
                self._content.setdefault('email', User.email)
            else:
                self._content.setdefault('email', '')
            if self._permisos[5]=='1' :
                self._content.setdefault('empresa', DatosPersonales.empresa)
            else:
                self._content.setdefault('empresa', '')
            if self._permisos[6]=='1' :
                self._content.setdefault('estatus', DatosPersonales.estatus)
            else:
                self._content.setdefault('estatus', '')
            if self._permisos[7]=='1' :
                self._content.setdefault('facebook',PaginasWeb.facebook)
            else:
                self._content.setdefault('facebook', '')
            if self._permisos[8]=='1' :
                self._content.setdefault('linkedin',PaginasWeb.linkedin)
            else:
                self._content.setdefault('linkedin', '')

            if self._permisos[9]=='1' :
                if DatosPersonales.nacimiento :
                    self._content.setdefault('nacimiento', DatosPersonales.nacimiento.isoformat())
                else:
                    self._content.setdefault('nacimiento', '')
            else:
                self._content.setdefault('nacimiento', '')

            if self._permisos[10]=='1' :
                self._content.setdefault('nombre', User.first_name)
            else:
                self._content.setdefault('nombre', '')

            if self._permisos[11]=='1' :
                self._content.setdefault('pais', DatosPersonales.pais)
            else:
                self._content.setdefault('pais', '')
            if self._permisos[12]=='1' :
                self._content.setdefault('profesion',DatosPersonales.profesion)
            else:
                self._content.setdefault('profesion', '')

            if self._permisos[13]=='1' :
                self._content.setdefault('telefono', DatosPersonales.telefono)
            else:
                self._content.setdefault('telefono', '')
            if self._permisos[14]=='1' :
                self._content.setdefault('twitter',PaginasWeb.twitter)
            else:
                self._content.setdefault('twitter', '')
            if self._permisos[15]=='1' :
                self._content.setdefault('webPersonal',PaginasWeb.webPersonal)
            else:
                self._content.setdefault('webPersonal', '')
            if self._permisos[16]=='1' :
                self._content.setdefault('webProfesional',PaginasWeb.webProfesional)
            else:
                self._content.setdefault('webProfesional', '')
            print self._content
            return self._content

        #Dado un conjunto de booleans crea una cadena de permisos
        def conversor(self, valor):
            cadena=array('c', ['0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0'])
            if valor.get('apellidos')==True:
                cadena[0]= '1'
            if valor.get('comentario')==True:
                cadena[1]='1'
            if valor.get('direccion')==True:
                cadena[2]='1'
            if valor.get('dni')==True:
                cadena[3]='1'
            if valor.get('email')==True:
                cadena[4]= '1'
            if valor.get('empresa')==True:
                cadena[5]='1'
            if valor.get('estatus')==True:
                cadena[6]= '1'
            if valor.get('facebook')==True:
                cadena[7]='1'
            if valor.get('linkedin')==True:
                cadena[8]= '1'
            if valor.get('nacimiento')==True:
                cadena[9]='1'
            if valor.get('nombre')==True:
                cadena[10]='1'
            if valor.get('pais')==True:
                cadena[11]= '1'
            if valor.get('profesion')==True:
                cadena[12]='1'
            if valor.get('telefono')==True:
                cadena[13]='1'
            if valor.get('twitter')==True:
                cadena[14]= '1'
            if valor.get('webPersonal')==True:
                cadena[15]= '1'
            if valor.get('webProfesional')==True:
                cadena[16]='1'
            return ''.join(cadena)

        def permisosToList(self):
            list=[]
            if self._permisos[0]=='1' :
                list.append('apellidos')
            if self._permisos[1]=='1' :
                list.append('comentario')
            if self._permisos[2]=='1' :
                list.append('direccion')
            if self._permisos[3]=='1' :
                list.append('dni')
            if self._permisos[4]=='1' :
                list.append('email')
            if self._permisos[5]=='1' :
                list.append('empresa')
            if self._permisos[6]=='1' :
                list.append('estatus')
            if self._permisos[7]=='1' :
                list.append('facebook')
            if self._permisos[8]=='1' :
                list.append('linkedin')
            if self._permisos[9]=='1' :
                list.append('nacimiento')
            if self._permisos[10]=='1' :
                list.append('nombre')
            if self._permisos[11]=='1' :
                list.append('pais')
            if self._permisos[12]=='1' :
                list.append('profesion')
            if self._permisos[13]=='1' :
                list.append('telefono')
            if self._permisos[14]=='1' :
                list.append('twitter')
            if self._permisos[15]=='1' :
                list.append('webPersonal')
            if self._permisos[16]=='1' :
                list.append('webProfesional')
            return list

        def elementosDisponibles(self):
            list=[]
            self._content={}
            if self._permisos[0]=='1' :
                list.append('apellidos')
            if self._permisos[1]=='1' :
                list.append('comentario')
            if self._permisos[2]=='1' :
                list.append('direccion')
            if self._permisos[3]=='1' :
                list.append('dni')
            if self._permisos[4]=='1' :
                list.append('email')
            if self._permisos[5]=='1' :
                list.append('empresa')
            if self._permisos[6]=='1' :
                list.append('estatus')
            if self._permisos[7]=='1' :
                list.append('facebook')
            if self._permisos[8]=='1' :
                list.append('linkedin')
            if self._permisos[9]=='1' :
                list.append('nacimiento')
            if self._permisos[10]=='1' :
                list.append('nombre')
            if self._permisos[11]=='1' :
                list.append('pais')
            if self._permisos[12]=='1' :
                list.append('profesion')
            if self._permisos[13]=='1' :
                list.append('telefono')
            if self._permisos[14]=='1' :
                list.append('twitter')
            if self._permisos[15]=='1' :
                list.append('webPersonal')
            if self._permisos[16]=='1' :
                list.append('webProfesional')
            self._content.setdefault('permisos',list)
            return self._content


        def __init__(self, stringPermisos):
            tam=len(stringPermisos)
            self._permisos=stringPermisos
            if tam<17:
                self._permisos = self._permisos+"00000000000000000"
