from django.shortcuts import render, get_object_or_404
from process.models import WorkerRecord

# Create your views here.
def render_plots(request):
    worker = get_object_or_404(WorkerRecord, id=int(request.GET.get('id', None)))
    return render(request, "plot/plots.html", {'worker': worker})