from .models import Process, WorkerRecord
from dataset.models import DataFile
from settings.settings import TEMP_FOLDER
from datetime import datetime
from threading import Thread
import os, importlib


class Worker(Thread):
    """ A process worker that runs and stores the resulted of the defined procedure
        @param process: The list of dictionary contains the whole process
        @param curr: the index of the current running function
        @param status: -1 suspended, 0 pending, 1 running, 2 finished
        @param id: the unique id indicating a running worker, used to retrieve
                   the worker
        @param annData: the annData in the memory going through each preprocess
    """

    def __init__(self, process, name):
        Thread.__init__(self)
        self.process = process
        self.curr = 0
        self.status = 0
        self.id = ""
        self.annData = None
        self.filename = None
        self.name = name

    def check_integrity(self):
        """ Check whether this process can run
        """

        # file-check
        reader = self.process[0]
        file_id = reader['params'].get('filename', None)
        if not file_id:
            return "Missing File", False
        self.filename = DataFile.objects.get(id=file_id).path
        if not self.filename:
            return {'info': "Missing File", 'status': False}

        wr = WorkerRecord(status=0,
                          curr=0,
                          total=len(self.process),
                          name=self.name)
        wr.save()
        self.id = wr.id
        if not os.path.isdir(TEMP_FOLDER):
            os.mkdir(TEMP_FOLDER)
        os.mkdir(os.path.join(TEMP_FOLDER, str(self.id)))
        index = 0
        for p in self.process:
            process = Process(wrid=self.id,
                              index=index,
                              call=p['package'] + "." + p['name'],
                              status=0,
                              time=datetime.now(),
                              output=""
                              )
            index += 1

            process.save()

        return {'info': self.name, 'status': True}

    def read_data(self):
        reader = self.process[0]

        params = reader['params'].copy()
        del params['filename']
        module = importlib.import_module(reader['package'])
        try:
            self.annData = getattr(module, reader['name'])(self.filename, **params, cache=True)
        except Exception as e:
            return (reader['package'] + "." + reader['name'],
                    params,
                    str(e),
                    2)

        return (reader['package'] + "." + reader['name'],
                params,
                str(self.annData),
                1)

    def proceed(self, process):
        """ Run the current process
        """
        module = importlib.import_module(process['package'])
        components = process['name'].split(".")
        for attr in components:
            module = getattr(module, attr)

        params = process['params'].copy()
        for key, value in process['params'].items():
            if value == "" or value == 0:
                del params[key]
        try:
            module(self.annData, **params)
        except Exception as e:
            return (process['package'] + "." + process['name'],
                    params,
                    str(e),
                    2)

        if process['view']:
            self.annData.write(os.path.join(TEMP_FOLDER, "resutls{curr}.h5ad".format(curr=str(self.curr))))

        return (process['package'] + "." + process['name'],
                params,
                str(self.annData),
                1)

    def log_adata(self, call, params, output, status):
        """ Print the log of the finished process
        """
        param_str = []
        for k, v in params.items():
            v = "\'" + v + "\'" if type(v) == str else str(v)
            param_str.append(str(k) + "=" + v)
        params = ", ".join(param_str)
        call = "{call}(target, {params})".format(call=call, params=params)

        log = Process.objects.get(wrid=self.id, index=self.curr)
        log.time = datetime.now()
        log.status = status
        log.output = output
        log.call = call
        log.save()

        if status == 1:
            self.curr += 1

        log_worker = WorkerRecord.objects.get(id=self.id)
        log_worker.time = datetime.now()
        log_worker.curr = self.curr
        log_worker.save()

    def run(self):
        self.log_adata(*self.read_data())
        curr = 1
        for process in self.process[1:]:
            if curr != self.curr:
                break
            self.log_adata(*self.proceed(process))
            curr += 1

        log_worker = WorkerRecord.objects.get(id=self.id)
        if self.curr == len(self.process):
            log_worker.status = 1
        else:
            log_worker.status = 2
        log_worker.save()
        try:
            self.annData.write(os.path.join(TEMP_FOLDER, str(self.id) + "/results.h5ad"))
        except AttributeError:
            pass
