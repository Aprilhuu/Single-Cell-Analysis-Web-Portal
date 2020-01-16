from django.shortcuts import render, get_object_or_404

from process.models import WorkerRecord, Process


# Create your views here.
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
    link = f'/userData/temp/{str(wrid)}/{output}.json'
    return render(request, "plot/plot-detail.html",
                  {'output': output,
                   'link': link,
                   'worker': get_object_or_404(WorkerRecord, id=wrid)
                   }
                  )
