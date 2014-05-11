from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^gcs/*', include('gcs.urls')),
    url(r'^comm/*', include('comm.urls')),
    url(r'^thebear/*', include('thebear.urls')),
    url(r'^uploader/*', include('uploader.urls')),
    url(r'^chatServer/*', include('chatServer.urls')),
    url(r'^admin/', include(admin.site.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
