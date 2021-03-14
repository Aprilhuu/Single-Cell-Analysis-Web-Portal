from SIMLR.settings import BASE_DIR
from process.CSQ_model import CSQLightening
import numpy as np
import os
import pandas as pd
import json


class ModelRun:
    def __init__(self, model_name):
        self.model_name = model_name
        self.check_pts_path = os.path.join(BASE_DIR, "pretrained_models", model_name, "checkpoint.ckpt")
        self.label_mapping = None

    # 计算hamming distance，B1是一组data，（一个vector），B2是一个matrix（所有database里的vector）
    @staticmethod
    def CalcHammingDist(B1, B2):
        q = B2.shape[1]
        distH = 0.5 * (q - np.dot(B1, B2.transpose()))
        return distH

    ## Initialize existing model
    def load_model(self):
        model = CSQLightening.load_from_checkpoint(checkpoint_path=self.check_pts_path,
                                                   n_class=13, n_features=17499, l_r=1.2e-5, lamb_da=0.001, beta=0.9999)
        with open(os.path.join(BASE_DIR, "pretrained_models", self.model_name, "label_mapping.json")) as f:
            self.label_mapping = json.load(f)
        return model

    # Predict label using Closest Hash Center strategy (b)
    def get_labels_pred_closest_hash_center(self, query_binaries, hash_centers):
        labels_pred = []
        for binary_query in query_binaries:
              dists = self.CalcHammingDist(binary_query, hash_centers)
              closest_class = np.argmin(dists)
              labels_pred.append(closest_class)

        return labels_pred

    def predict(self, query_data):
        model = self.load_model()
        binary_predict = model.forward(query_data).sign()
        labels_pred_CHC = self.get_labels_pred_closest_hash_center(binary_predict.detach().numpy(),
                                                                   model.hash_centers.numpy())
        string_labels = [self.label_mapping[str(int_label)] for int_label in labels_pred_CHC]
        return string_labels, binary_predict.detach().numpy(), model.hash_centers.numpy()

if __name__ == '__main__':
    import torch
    new_model = ModelRun("BaronHuman")

    DataPath = os.path.join(BASE_DIR, "pretrained_models", "BaronHuman", "Filtered_Baron_HumanPancreas_data.csv")
    data = pd.read_csv(DataPath, index_col=0, sep=',', nrows=30)
    full_data = np.asarray(data, dtype=np.float32)
    input_data = torch.from_numpy(full_data)
    labels = new_model.predict(input_data)
    print(labels)
