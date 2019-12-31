from django.urls import path

from . import views

urlpatterns = [
    path('', views.render_plots),
    path('plots.html', views.render_plots)
]
