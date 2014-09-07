from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout, name='logout'),
    url(r'^newUser', views.newUser, name='newUser'),
    url(r'^authUserHandler', views.authUserHandler, name='authUserHandler'),
)
