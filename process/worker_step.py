from .models import Process
import importlib, os
from settings.settings import TEMP_FOLDER


class WorkerStep:
    """
    One step in a worker, manage the logging and running of one step
    @:param context: an dictionary object contains the function call
    @:param call: a string of the function call
    @:param output: a string of the function call's output
    @:param status: the status of this step
    @:param file: the associated file of this step, if needed
    """

    def __init__(self, context, wrid, index, file, annData):
        self.context = context
        self.output = ""
        self.status = 0
        self.wrID = wrid
        self.index = index
        self.file = file
        self.annData = annData

    def run(self):
        return NotImplementedError("Abstract class")

    def log(self):
        """ Print the log of the finished process
        """
        param_str = []
        params = self.context['params']
        for k, v in params.items():
            v = "\'" + v + "\'" if type(v) == str else str(v)
            param_str.append(str(k) + "=" + v)
        params = ", ".join(param_str)

        call = self.context['package'] + "." + self.context['name']
        log = Process.objects.get(wrid=self.wrID, index=self.index)
        log.status = self.status
        log.output = self.output
        log.call = "{call}(target, {params})".format(call=call, params=params)
        log.save()


class ReaderStep(WorkerStep):

    def run(self):
        params = self.context['params']
        del params['filename']
        module = importlib.import_module(self.context['package'])
        try:
            self.annData = getattr(module, self.context['name'])(self.file, **params, cache=True)
        except Exception as e:
            self.output = str(e)
            self.status = 2
            self.log()
            return
        self.output = str(self.annData)
        self.status = 1
        self.log()


class ProcessingStep(WorkerStep):

    def run(self):
        module = importlib.import_module(self.context['package'])
        components = self.context['name'].split(".")
        for attr in components:
            module = getattr(module, attr)

        params = self.context['params'].copy()
        for key, value in self.context['params'].items():
            if value == "" or value == 0:
                del params[key]
        self.context['params'] = params
        try:
            module(self.annData, **params)
        except Exception as e:
            self.output = str(e)
            self.status = 2
            self.log()
            return

        if self.context['view']:
            self.annData.write(os.path.join(TEMP_FOLDER,
                                            os.path.join(str(self.wrID),
                                                         "/views_{index}.h5ad".format(index=self.index))))

        self.output = str(self.annData)
        self.status = 1
        self.log()
