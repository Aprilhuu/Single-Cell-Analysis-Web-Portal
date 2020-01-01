from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.shortcuts import render

from .models import Methods


# Create your views here.

def render_installed_methods(request):
    return render(request, "settings/installed-methods.html")


def get_installed_methods(request):
    if request.method == "GET":
        type = request.GET.get("type", "")
        name = request.GET.get("name", "")
        if type == "_all" and name == "_all":
            read_json = Methods.objects.all()
        elif type == "_all":
            read_json = Methods.objects.filter(name=name)
        elif name == "_all":
            read_json = Methods.objects.filter(type=type)
        else:
            read_json = Methods.objects.filter(name=name, type=type)
        read_json = [m.assembly() for m in read_json]
        return JsonResponse(read_json, safe=False)
    if request.method == "POST":
        action = request.POST.get('action', "")
        id = request.POST.get("id", None)
        if action != "DELETE" or not id:
            return HttpResponseForbidden()
        Methods.objects.get(id=id).delete()
        return JsonResponse({'id': id})
    return Http404


def add_installed_methods(request):
    saved_method = Methods(
        type=request.POST.get('type'),
        package=request.POST.get('package'),
        name=request.POST.get('name'),
        description=request.POST.get('description'),
        params=str(request.POST.get('params', ""))
    )
    saved_method.save()
    return JsonResponse(saved_method.assembly(), safe=False)
