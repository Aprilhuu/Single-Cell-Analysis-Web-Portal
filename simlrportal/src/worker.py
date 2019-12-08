from simlrportal.models.models import *
from simlrportal import app
from datetime import datetime
from threading import Thread
import json, uuid, os, importlib



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
            return ("Missing File", False)
        self.filename = DataFile.query.filter_by(id=file_id).first().path
        if not self.filename:
            return {'info': "Missing File", 'status' : False}

        self.id = uuid.uuid4().hex
        while os.path.exists(app.config['TEMP_FOLDER'] + self.id):
            self.id = uuid.uuid4().bytes
        os.mkdir(app.config['TEMP_FOLDER'] + self.id)


        # commit to db
        index = 0
        for p in self.process:
            process = Process( id = self.id,
                               index = index,
                               call = p['package'] + "." + p['name'],
                               status = 0,
                               time = datetime.now(),
                               output = ""
                              )
            db.session.add(process)
            index += 1
        wr = WorkerRecord( id = self.id,
                           status = 0,
                           time = datetime.now(),
                           curr = 0,
                           total = len(self.process),
                           name = self.name
                         )
        db.session.add(wr)

        db.session.commit()

        return {'info': self.name, 'status': True}


    def read_data(self):
        reader = self.process[0]

        params = reader['params'].copy()
        del params['filename']
        module = importlib.import_module(reader['package'])
        try:
            self.annData = getattr(module, reader['name'])(self.filename, **params, cache=True)
        except Exception as e:
            return ( reader['package'] + "." + reader['name'],
                     params,
                     str(e),
                     2 )

        return ( reader['package'] + "." + reader['name'],
                 params,
                 str(self.annData),
                 1 )


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
            return ( process['package'] + "." + process['name'],
                     params,
                     str(e),
                     2 )

        if process['view']:
            self.annData.write(app.config['TEMP_FOLDER'] + "resutls{curr}.h5ad".format(curr=str(self.curr)))

        # self.curr += 1
        return ( process['package'] + "." + process['name'],
                 params,
                 str(self.annData),
                 1 )


    def log_adata(self, call, params, output, status):
        """ Print the log of the finished process
        """
        params = ", ".join([str(k) + "=" + str(v) for k, v in params.items()])
        call = "{call}(target, {params})".format(call=call, params=params)


        log = Process.query.filter_by(id=self.id, index=self.curr).first()
        log.time = datetime.now()
        log.status = status
        log.output = output
        log.call = call

        self.curr += 1

        log_worker = WorkerRecord.query.filter_by(id=self.id).first()
        log_worker.time = datetime.now()
        log_worker.curr = self.curr

        db.session.commit()



    def run(self):
        self.log_adata(*self.read_data())
        curr = 1
        for process in self.process[1:]:
            if curr != self.curr:
                break
            self.log_adata(*self.proceed(process))
            curr += 1

        log_worker = WorkerRecord.query.filter_by(id=self.id).first()
        if self.curr == len(self.process):
            log_worker.status = 1
        else:
            log_worker.status = 2
        db.session.commit()
        try:
            self.annData.write(app.config['TEMP_FOLDER'] + self.id +"/resutls.h5ad")
        except AttributeError:
            pass
