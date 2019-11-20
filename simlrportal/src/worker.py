import importlib
import os
from simlrportal.models.models import DataFile

class Worker:
    """ A process worker that runs and stores the resulted of the defined procedure
        @param process: The list of dictionary contains the whole process
        @param curr: the index of the current running function
        @param status: -1 suspended, 0 pending, 1 running, 2 finished
        @param id: the unique id indicating a running worker, used to retrieve
                   the worker
        @param annData: the annData in the memory going through each preprocess
    """
    def __init__(self, process):
        self.process = process
        self.curr = 0
        self.status = 0
        self.id = ""
        self.annData = None

    def check_integrity(self):
        """ Check whether this process can run
        """

        # for i in range(len(self.process)):
        #     # check whether all prerequisites are installed
        #     for i in self.process[i].get("prerequisites", []):
        #         prereq_check = False
        #         for j in self.process[:i]:
        #             if i['name'] == j['name'] and i['package'] == j['package']:
        #                 prereq_check = True
        #                 break
        #         if not prereq_check:
        #             return ("prerequisite not satisfied: " + i['name'] + "." i['package'], False)

        return ("", True)


    def read_data(self):
        reader = self.process[0]
        file_id = reader['params']['filename']
        filepath = DataFile.query.filter_by(id=file_id).first().path

        params = reader['params'].copy()
        del params['filename']
        module = importlib.import_module(reader['package'])
        self.annData = getattr(module, reader['name'])(filepath, **params)



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

        module(self.annData, **params)
        print(process['package'], process['name'])

    def run(self):
        self.read_data()
        for process in self.process[1: ]:
            self.proceed(process)
            self.curr += 1
