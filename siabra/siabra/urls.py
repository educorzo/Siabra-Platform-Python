from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'siabra.views.home', name='home'),
    # url(r'^siabra/', include('siabra.foo.urls')),
    # url(r'^$',PaginaPrincipal.as_view(), name='wellcome' ),
    url(r'^$','principal.views.welcome',name='welcome'),
    url(r'^eliminado/(?P<parametro>\d+)','principal.views.welcome'),
    url(r'^home/','principal.views.home',name='home'),
    url(r'^documentacion/','principal.views.documentacion',name='documentacion'),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^oauth/', include('oauth_provider.urls')),#CONTROLADOR CAPTCHA
    url(r'^captcha/', include('captcha.urls')), #CONTROLADOR OAUTH
    url(r'^admin/', include(admin.site.urls), name='admin'),#ADMINISTRADOR
    url(r'^cerrar/$', 'principal.views.cerrar'), #LOGOUT
    url(r'^accounts/login/', 'principal.views.loginAuthorize', name='loginAuthorize'),#LOGIN APP
    url(r'^datos','principal.views.modificar_datos_personales', name='datos'),#FORMULARIO
    url(r'^perfil/modificar','principal.views.crear_perfil', name='crearPerfil'), #FORMULARIO
    url(r'^aplicacion/modificar','principal.views.crear_aplicacion', name='crearAplicacion'),#FORMULARIO
    url(r'^paginasweb/modificar','principal.views.modificar_paginas_web',name='modificarPaginas'),#FORMULARIO
    url(r'^imagen/add','principal.views.add_imagen',name='addImagen'),#ADD
    url(r'^acerca/','principal.views.acerca',name='acerca'),
    url(r'^informacion/','principal.views.acerca_no_logueado',name='acercaNoLog'),
    #REST
    url(r'^check/','principal.rest.check'),
    url(r'^user/show/','principal.rest.user', name='user'),#GET
    url(r'^user/other/','principal.rest.other',name='otroUser'),#GET
    url(r'^perfil/show/','principal.rest.perfil', name='perfil'),#GET
    url(r'^perfil/list/','principal.rest.listaPerfil', name='listaPerfil'),#GET
    url(r'^perfil/new/','principal.rest.nuevoPerfil',name='nuevoPerfil'),#POST
    url(r'^perfil/cancel/','principal.rest.cancelarPerfil',name='cancelarPerfil'),#POST
    url(r'^permisos/show/code/','principal.rest.permisos', name='permisos'),#GET
    url(r'^permisos/show/words/','principal.rest.permisosPorPalabras', name='permisosPorPalabras'),#GET
    url(r'^permisos/modify/code/','principal.rest.modificarPermisos', name='modificarPermisos'),#POST
    url(r'^permisos/modify/words/','principal.rest.modificarPermisosPorPalabras', name='modificarPermisosPorPalabras'),#POST
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    url(r'^i18n/', include('django.conf.urls.i18n')),

)
urlpatterns += staticfiles_urlpatterns()
