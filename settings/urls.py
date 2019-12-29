from django.urls import path

from . import views

urlpatterns = [
    path('installed-methods', views.get_installed_methods)
]
