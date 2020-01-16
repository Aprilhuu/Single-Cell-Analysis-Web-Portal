from django.urls import path

from . import views

urlpatterns = [
    path('', views.render_plots),
    path('plots.html', views.render_plots),
    path('plot-detail.html', views.render_plot_detail)
]
