from django.shortcuts import render, get_object_or_404
from .models import *
from shutil import rmtree
import os, json
from settings.settings import TEMP_FOLDER
from django.http import JsonResponse
from .worker import Worker

def render_newprocess(request):
    return render(request, "newprocess.html")


def render_process(request):
    worker = get_object_or_404(WorkerRecord, id=int(request.GET.get('id', None)))
    return render(request, "process.html", {'worker': worker})


def render_process_history(request):
    return render(request, "process-history.html")


def get_process_history(request):
    if request.method == 'GET':
        name = request.GET.get("name", "")
        if name == "_all":
            result = WorkerRecord.objects.all()
        else:
            result = Process.objects.filter(wrid=name)
        return JsonResponse(list(result.values()), safe=False)

    if request.method == 'POST' and request.POST.get('action') == 'DELETE':
        id = request.POST.get("id", "")
        WorkerRecord.objects.filter(id=id).delete()
        Process.objects.filter(wrid=id).delete()
        try:
            rmtree(os.path.join(TEMP_FOLDER, id))
        except FileNotFoundError:
            pass

        return JsonResponse({'id': id, 'status': 'success'})


def post_new_process(request):
    process = json.loads(request.POST.get('process'))
    worker = Worker(process, request.POST.get('name'))
    integrity = worker.check_integrity()
    if integrity['status']:
        worker.start()
    return JsonResponse(integrity)
