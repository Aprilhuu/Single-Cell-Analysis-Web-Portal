from django.urls import path

from . import views

urlpatterns = [
    path('dataupload.html', views.render_dataupload),
    path('datasets.html', views.render_dataset),
    path('datasets', views.rest_datasets),
    path('data-upload', views.data_upload)
]
