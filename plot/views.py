from django.shortcuts import render, get_object_or_404

from process.models import WorkerRecord, Process


# Create your views here.
def render_plots(request):
    return render(request, "plot/plots.html",
                  {'worker': get_object_or_404(WorkerRecord, id=int(request.GET.get('id', None))),
                   "plots": Process.objects.filter(type__in=["plot", "iplot"],
                                                   wrid=int(request.GET.get('id', None)),
                                                   status=1)})
