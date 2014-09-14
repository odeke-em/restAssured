from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^logout', views.logout, name='logout'),
    url(r'^newUser', views.newUser, name='newUser'),
    url(r'^appHandler', views.appHandler, name='appHandler'),
    url(r'^passToLogin', views.loginByPassword, name='passToLogin'),
    url(r'^signToLogin', views.loginBySignature, name='signToLogin'),
    url(r'^authUserHandler', views.authUserHandler, name='authUserHandler'),
)
