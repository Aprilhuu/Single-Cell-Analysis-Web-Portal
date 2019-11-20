class Module:
    """ Interface for modules,
        For each implementation of this class, make sure the class name is unique
    """
    def __init__(self):
        self.progress = -1

    def get_progress(self):
        """ Return the progress as a int between -1 and 100
            -1 stands for not implemented, and will be ignored by the frontend
        """
        return self.progress

    def update_progress(self):
        """ Set the progress
        """
        raise NotImplementedError("update_progress: not implemented")


    def run(self, params):
        """ Run the preprocesses function given the parameters

            params:   dict - The dictionary of all parameters necessary for the
                             function to run. Each key-value pair will be one
                             parameter specified

            @return:  In most cases, return None, and the preprocess will be
                      applied to the AnnData. If view is specified, then return
                      the wanted DataFrames
        """
        raise NotImplementedError("run: not implemented")


    def set_prerequisite(self, prereq):
        """ Specify the prerequisites when this method must be ran after some
            other methods,

            prereq: A list of string of prerequisite class that must be run
                    before this
        """
        pass
