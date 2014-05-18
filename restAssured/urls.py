from django.conf import settings
from django.conf.urls import patterns, include, url, static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^gcs/*', include('gcs.urls')),
    # url(r'^comm/*', include('comm.urls')),
    (r'^thebear/*', include('thebear.urls')),
    (r'^uploader/*', include('uploader.urls')),
    (r'^chatServer/*', include('chatServer.urls')),
    (r'^admin/', include(admin.site.urls)),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
) + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
