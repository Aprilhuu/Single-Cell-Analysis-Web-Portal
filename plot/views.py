import json
import os

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from scanpy import read_h5ad

import iplot
from dataset.models import DataSet
from process.models import WorkerRecord, Process
from settings.settings import USER_PROCESS_FOLDER


def render_plots(request):
    return render(request, "plot/plots.html",
                  {'worker': get_object_or_404(WorkerRecord, id=int(request.GET.get('id', None))),
                   "plots": Process.objects.filter(type__in=["plot", "iplot"],
                                                   wrid=int(request.GET.get('id', None)),
                                                   status=1)})


def render_plot_detail(request):
    wrid = request.GET.get('id', None)
    output = request.GET.get('output', "").rsplit(".", 1)[0]
    if wrid is not None and len(output) < 2:
        return
    link = f'/userData/processes/{str(wrid)}/{output}.json'
    return render(request, "plot/plot-detail.html",
                  {
                      'output': output,
                      'link': link,
                      'worker': get_object_or_404(WorkerRecord, id=wrid)
                  }
                  )


def render_plot_studio(request):
    id_ = int(request.GET.get('id', None))
    if id_ is None:
        return HttpResponseBadRequest
    worker = get_object_or_404(WorkerRecord, id=int(id_))
    dataset = get_object_or_404(DataSet, name=f"Worker_{id_}")
    return render(request, "plot/plot-studio.html",
                  {'worker': worker,
                   "dataset": dataset})


def render_plot_studio_detail(request):
    id_ = int(request.POST.get('id', -1))
    call = request.POST.get('call', {})
    param = request.POST.get('params', None)
    param = json.loads(param) if param is not None else {}
    if id_ == -1 or call is None:
        return HttpResponseBadRequest
    adata = read_h5ad(os.path.join(USER_PROCESS_FOLDER, str(id_), "results.h5ad"))
    module = iplot
    for part in call.split("."):
        module = getattr(module, part)
    return JsonResponse(module(adata, **param), safe=False)
