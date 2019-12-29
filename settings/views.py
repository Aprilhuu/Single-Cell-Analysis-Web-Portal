from django.shortcuts import render
from django.http import JsonResponse, Http404
from .settings import *


# Create your views here.

def get_installed_methods(request):
    if request.method == "GET":
        type = request.GET.get("type", "")
        name = request.GET.get("name", "")
        if name == "_all":
            f = open(INSTALLED_METHODS_PATH[type], "r")
            read_json = f.read()
            f.close()
            return JsonResponse(read_json, safe=False)
    return Http404
