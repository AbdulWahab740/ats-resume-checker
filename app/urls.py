from django.urls import path

from . import views

urlpatterns = [
    path("",views.index,name='home'),
    path("upload-docs", views.upload_docs, name="upload_docs"),
]

from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)