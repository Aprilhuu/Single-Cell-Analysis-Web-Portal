class Worker:
    """ A process worker that runs and stores the resulted of the defined procedure
        @param process: The dictionary contains the whole process
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

        for i in range(len(self.process)):
            # check whether all prerequisites are installed
            for i in self.process[i].get("prerequisites", []):
                prereq_check = False
                for j in self.process[:i]:
                    if i['name'] == j['name'] and i['package'] == j['package']:
                        prereq_check = True
                        break
                if not prereq_check:
                    return ("prerequisite not satisfied: " + i['name'] + "." i['package'], False)

        return ("", True)
