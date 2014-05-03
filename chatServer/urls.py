from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^/', views.messageHandler, name='messageHandler'),
    url(r'^messageHandler', views.messageHandler, name='messageHandler'),
    url(r'^receipientHandler', views.receipientHandler, name='receipientHandler'),
    url(r'^messageMarkerHandler', views.messageMarkerHandler, name='messageMarkerHandler'),
)
