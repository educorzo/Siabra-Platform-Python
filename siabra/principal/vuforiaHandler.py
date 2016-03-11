#encoding:utf-8
from array import *
from django.core.exceptions import ObjectDoesNotExist
import uuid
import urlparse
import requests
import datetime
import os
import hashlib
import hmac
import base64
import json

class VuforiaHandler():
    key='31ed86c915609c99fd8e5070dc4d2db60841c1b4'
    secret='0482628e25aec64fd5956c577db965113ecdddb3'
    url='https://vws.vuforia.com/targets'

    def __init__(self):
        os.environ['TZ'] = 'Africa/Bissau'

    def subirImagen(self,name,imagen):
        contentMD5 = hashlib.md5()
        now = datetime.datetime.now()
        fecha= now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        image64= imagen.read().encode('base64')
        image64=image64.replace("\n","") #Diferencias entre encode de php y python
        image64=image64.replace("/","\/")#Diferencias entre encode de php y python
        cadena='{"width":6,"name":"'+name+'","image":"'+image64+'","active_flag":1}'
        contentMD5.update(str(cadena))
        stringtoSign='POST'+'\n'+contentMD5.hexdigest()+'\n'+'application/json'+'\n'+fecha+'\n'+'/targets'
        signature= hmac.new(self.secret, stringtoSign, hashlib.sha1).digest()
        signature = base64.b64encode(signature)
        autorizacion='VWS %s:%s' % (self.key, signature)
        headers = {'Date':fecha,'Content-Type': 'application/json','Authorization':autorizacion}
        response =requests.post(self.url, data=cadena, headers=headers)
        return response

    def desactivarImagen(self,name,target_id):
        contentMD5 = hashlib.md5()
        now = datetime.datetime.now()
        fecha= now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        cadena='{"name":"' +name+ '","active_flag":0}'
        contentMD5.update(str(cadena))
        stringtoSign='PUT'+'\n'+contentMD5.hexdigest()+'\n'+'application/json'+'\n'+fecha+'\n'+'/targets/'+target_id
        self.url=self.url+"/"+target_id
        signature= hmac.new(self.secret, stringtoSign, hashlib.sha1).digest()
        signature = base64.b64encode(signature)
        autorizacion='VWS %s:%s' % (self.key, signature)
        headers = {'Date':fecha,'Content-Type': 'application/json','Authorization':autorizacion}
        response =requests.put(self.url, data=cadena, headers=headers)
        return response

    def eliminarImagen(self,target_id):
        now = datetime.datetime.now()
        fecha= now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        stringtoSign='DELETE'+'\n'+"d41d8cd98f00b204e9800998ecf8427e"+'\n'+'\n'+fecha+'\n'+'/targets/'+target_id
        print stringtoSign
        url=url+"/"+target_id
        signature= hmac.new(self.secret, stringtoSign, hashlib.sha1).digest()
        signature = base64.b64encode(signature)
        autorizacion='VWS %s:%s' % (self.key, signature)
        headers = {'Date':fecha,'Authorization':autorizacion}
        response =requests.delete(url, headers=headers)
        return response
