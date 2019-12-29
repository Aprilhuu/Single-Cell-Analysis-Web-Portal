from django.urls import path

from . import views

urlpatterns = [
    path('', views.render_newprocess),
    path('process.html', views.render_process),
    path('newprocess.html', views.render_newprocess),
    path('process-history.html', views.render_process_history),
    path('process-history', views.get_process_history),
    path('new-process', views.post_new_process)
]
