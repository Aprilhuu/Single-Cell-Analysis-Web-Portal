from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest
from settings.settings import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from .models import DataFile
from time import time

from shutil import rmtree, unpack_archive, get_archive_formats
import os


def render_dataset(request):
    return render(request, "dataset/datasets.html")


def render_dataupload(request):
    return render(request, "dataset/dataupload.html",
                  {'allowed_file': ", ".join(ALLOWED_EXTENSIONS)})


def rest_datasets(request):
    if request.method == 'GET':
        limit = int(request.GET.get('limit', 0))
        offset = int(request.GET.get('offset', 0))
        result =  DataFile.objects.all()[offset: limit]
        return JsonResponse(list(result.values()), safe=False)
    if request.method == "POST":
        action = request.POST.get('action', "")
        id = request.POST.get("id", None)
        if action != "DELETE" or not id:
            return HttpResponseForbidden()
        try:
            result = DataFile.objects.get(id=id)
            if os.path.isfile(result.path):
               os.remove(result.path)
            if os.path.isdir(result.path):
               rmtree(result.path)
            result.delete()
            return JsonResponse({'id': id})
        except DataFile.DoesNotExist:
            return Http404


def dataupload(request):
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    file = request.FILES.get('file', None)
    if not file:
        return HttpResponseBadRequest
    file_ori, ext = file.name.rsplit('.', 1)
    ext = ext.lower()
    hash_name = file_ori + "_" + hex(int(time()))
    path = os.path.join(UPLOAD_FOLDER, hash_name + "." + ext)

    with open(path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)

    if ext in [x[0] for x in get_archive_formats()]:
        unpack_archive(path, os.path.join(UPLOAD_FOLDER))
        os.rename(os.path.join(UPLOAD_FOLDER, file_ori),
                  os.path.join(UPLOAD_FOLDER, hash_name))
        os.remove(path)
        path = os.path.join(UPLOAD_FOLDER, hash_name)

    saved_file = DataFile(
        source = request.POST.get("owner", "Upload"),
        name = request.POST.get("name", "uploaded-file"),
        path = path,
        description = request.POST.get("description", "")
    )
    saved_file.save()
    return JsonResponse({'name': saved_file.name})