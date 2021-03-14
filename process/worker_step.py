import importlib
import json
import os
import traceback

from settings.settings import USER_PROCESS_FOLDER
from .models import Process


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
        self.folder = os.path.join(USER_PROCESS_FOLDER, str(self.wrID))

    def run(self):
        return NotImplementedError("Abstract class")

    def parse_call(self):
        module = importlib.import_module(self.context['package'])
        components = self.context['name'].split(".")
        for attr in components:
            module = getattr(module, attr)
        params = self.context['params'].copy()
        for key, value in self.context['params'].items():
            if value == "" or value == 0:
                del params[key]
        return module, params, components

    def log(self):
        """ Print the log of the finished process
        """
        param_str = []
        params = self.context['params']
        params.pop('filename', None)
        for k, v in params.items():
            v = "\'" + v + "\'" if type(v) == str else str(v)
            param_str.append(str(k) + "=" + v)
        params = ", ".join(param_str)

        call = self.context['package'] + "." + self.context['name']
        log = Process.objects.get(wrid=self.wrID, index=self.index)
        log.status = self.status
        log.output = self.output
        log.call = f"{call}(target, {params})"
        log.save()


class ReadStep(WorkerStep):

    def __init__(self, context, wrid, index, file, annData, subset=None):
        WorkerStep.__init__(self, context, wrid, index, file, annData)
        self.subset = subset

    def run(self):
        module, params, _ = self.parse_call()
        del params['filename']
        try:
            self.annData = module(self.file, **params)
            if self.subset is not None:
                self.annData = self.annData[self.subset, :]
        except Exception as e:
            self.output = str(e)
            self.status = 2
            self.log()
            return
        self.output = str(self.annData)
        self.status = 1
        self.log()


class ProcessStep(WorkerStep):
    def run(self):
        module, params, _ = self.parse_call()
        self.context['params'] = params
        try:
            module(self.annData, **params)
        except Exception:
            self.output = traceback.print_exc()
            self.status = 2
            self.log()
            return

        if self.context.get('view', None):
            self.annData.write(os.path.join(self.folder, f'views_{self.index}.h5ad'))

        self.output = str(self.annData)
        self.status = 1
        self.log()


class PlotStep(WorkerStep):
    def parse_call(self):
        module = importlib.import_module(self.context['package'])
        if self.context['package'] == "scanpy":
            module._settings.settings.figdir = self.folder
        components = self.context['name'].split(".")
        for attr in components:
            module = getattr(module, attr)
        params = self.context['params'].copy()
        for key, value in self.context['params'].items():
            if value == "" or value == 0:
                del params[key]
        return module, params, components

    def run(self):
        module, params, components = self.parse_call()
        self.context['params'] = params
        try:
            module(self.annData,
                   **params,
                   save=f'plot_{self.index}.png',
                   show=False)
        except Exception as e:
            self.output = str(e)
            self.status = 2
            self.log()
            return

        self.output = f"{components[-1]}plot_{self.index}.png"
        self.status = 1
        self.log()


class IPlotStep(WorkerStep):
    def run(self):
        module, params, components = self.parse_call()
        self.context['params'] = params
        try:
            with open(os.path.join(self.folder, f"{components[-1]}plot_{self.index}.json"), "w") as f:
                json.dump(module(self.annData,
                                 **params,
                                 save=os.path.join(self.folder, f"{components[-1]}plot_{self.index}.png")),
                          f)
        except Exception as e:
            self.output = str(e)
            self.status = 2
            self.log()
            return

        self.output = f"{components[-1]}plot_{self.index}.png"
        self.status = 1
        self.log()


class ClassificationStep(WorkerStep):
    def run(self):
        import numpy as np
        from .model_run import ModelRun
        import torch

        try:
            prediction_process = ModelRun(model_name=self.context["name"])

            # # TODO: Remove this after testing
            # self.annData = self.annData[0:100]

            query_data = self.annData.X
            input_data = torch.from_numpy(query_data)
            labels, full_hash_codes, hash_centers = prediction_process.predict(input_data)
            full_labels = np.asarray(labels)

            self.annData.obs["csq_classifier"] = full_labels
            self.annData.obs["csq_classifier"] = self.annData.obs["csq_classifier"].astype('category')

            self.annData.uns["csq_binary_hash"] = full_hash_codes
            self.annData.uns["hash_centers"] = hash_centers

        except Exception as e:
            self.output = str(e)
            self.status = 2
            self.log()
            return
        self.output = str(self.annData)
        self.status = 1
        self.log()


class CSQStep(WorkerStep):
    def run(self):
        import anndata
        import scanpy
        import numpy as np

        try:
            visualize_method = self.context["name"]
            binary_hash = anndata.AnnData(X=self.annData.uns["csq_binary_hash"])
            binary_hash.obs_names = self.annData.obs_names
            print(self.annData.obs["csq_classifier"])
            print(binary_hash)
            binary_hash.obs["csq_binary_hash"] = self.annData.obs["csq_classifier"]

            if visualize_method == "tsne":
                scanpy.tl.tsne(binary_hash)
            elif visualize_method == "pca":
                scanpy.tl.pca(binary_hash)
            elif visualize_method == "umap":
                scanpy.tl.umap(binary_hash)
            else:
                raise RuntimeError("Unrecognized visualization method " + visualize_method)

            #placeholders = np.ones((self.annData.shape[0], ))

            #self.annData.obs["csq_binary_hash"] = placeholders
            #self.annData.obs["csq_binary_hash"] = self.annData.obs["csq_binary_hash"].astype('category')

            path = os.path.join(USER_PROCESS_FOLDER, str(self.wrID), "binary_hash.h5ad")
            binary_hash.write(path)

        except Exception as e:
            self.output = str(e)
            self.status = 2
            self.log()
            return
        self.output = str(self.annData)
        self.status = 1
        self.log()