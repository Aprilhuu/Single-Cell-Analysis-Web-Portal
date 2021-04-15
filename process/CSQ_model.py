import torch
from torch import nn
import pytorch_lightning as pl
from sklearn.metrics import f1_score

from collections import Counter
import statistics
# direct import  hadamrd matrix from scipy
from scipy.linalg import hadamard
import numpy as np

###--------------------------Utility functions-------------------------------###
# use algorithm 1 to generate hash centers
def get_hash_centers(n_class, bit):
    H_K = hadamard(bit)
    H_2K = np.concatenate((H_K, -H_K), 0)
    hash_targets = torch.from_numpy(H_2K[:n_class]).float()

    if H_2K.shape[0] < n_class:
        hash_targets.resize_(n_class, bit)
        for k in range(20):
            for index in range(H_2K.shape[0], n_class):
                ones = torch.ones(bit)
                # Bernouli distribution
                sa = random.sample(list(range(bit)), bit // 2)
                ones[sa] = -1
                hash_targets[index] = ones
            # to find average/min  pairwise distance
            c = []
            for i in range(n_class):
                for j in range(n_class):
                    if i < j:
                        TF = sum(hash_targets[i] != hash_targets[j])
                        c.append(TF)
            c = np.array(c)

            # choose min(c) in the range of K/4 to K/3
            # see in https://github.com/yuanli2333/Hadamard-Matrix-for-hashing/issues/1
            # but it is hard when bit is  small
            if c.min() > bit / 4 and c.mean() >= bit / 2:
                print(c.min(), c.mean())
                break
    return hash_targets


# Needs to add algorithm 2 to generate hash centers


# 计算所有metrics的top-level interface
def compute_metrics(database_dataloader, query_dataloader, net, top_k, class_num):
    ''' Labeling Strategy:

    (a) Majority Vote:
    Label the query using the majority labels in the top K nearest
    (in hamming space) cells in the database.
    - Computation Complexity:
      O(nlogK) per query   --> Current implementation O(nlogn)
      n = number of cells in database
    - Very Accurate

    (b) Closest Hash Center:
    Label the query using the label associated to the nearest hash center
    - Computation Complexity:
      O(m) << O(n) per puery
      m = number of classes in database
    - Less Accurate
    '''

    binaries_database, labels_database = compute_result(database_dataloader, net)
    binaries_query, labels_query = compute_result(query_dataloader, net)

    # 转换成one-hot encoding，方便后续高效计算
    labels_database_one_hot = categorical_to_onehot(labels_database, class_num)
    labels_query_one_hot = categorical_to_onehot(labels_query, class_num)

    # (1) MAP, *****默认给所有得到的average precisions排序，top_k = -1*****
    MAP = compute_MAP(binaries_database.cpu().numpy(), binaries_query.cpu().numpy(),
                      labels_database_one_hot.numpy(), labels_query_one_hot.numpy(), -1)

    # 根据自定义的labeling策略，得到预测的labels
    labels_pred_KNN = get_labels_pred_KNN(binaries_database.cpu().numpy(), binaries_query.cpu().numpy(),
                                          labels_database_one_hot.numpy(), labels_query_one_hot.numpy(), top_k)
    labels_pred_CHC = get_labels_pred_closest_hash_center(binaries_query.cpu().numpy(), labels_query.numpy(),
                                                          net.hash_centers.numpy())

    # (2) 自定义的labeling策略的accuracy
    labeling_accuracy_KNN = compute_labeling_strategy_accuracy(labels_pred_KNN, labels_query_one_hot.numpy())
    labeling_accuracy_CHC = compute_labeling_strategy_accuracy(labels_pred_CHC, labels_query.numpy())

    # (3) F1_score, average = (micro, macro, weighted)
    F1_score_weighted_average_KNN = f1_score(labels_query_one_hot, labels_pred_KNN, average='weighted')
    F1_score_per_class_KNN = f1_score(labels_query_one_hot, labels_pred_KNN, average=None)

    F1_score_weighted_average_CHC = f1_score(labels_query, labels_pred_CHC, average='weighted')
    F1_score_per_class_CHC = f1_score(labels_query, labels_pred_CHC, average=None)

    # (4) F1_score的中位数
    F1_score_per_class_median_KNN = statistics.median(F1_score_per_class_KNN)
    F1_score_per_class_median_CHC = statistics.median(F1_score_per_class_CHC)

    KNN_metrics = (
    labeling_accuracy_KNN, F1_score_weighted_average_KNN, F1_score_per_class_median_KNN, F1_score_per_class_KNN)
    CHC_metrics = (
    labeling_accuracy_CHC, F1_score_weighted_average_CHC, F1_score_per_class_median_CHC, F1_score_per_class_CHC)

    return MAP, KNN_metrics, CHC_metrics


# 了解Top K原理的链接：https://towardsdatascience.com/breaking-down-mean-average-precision-map-ae462f623a52
def compute_MAP(retrieval_binaries, query_binaries, retrieval_labels, query_labels, topk):
    num_query = query_labels.shape[0]
    topK_ave_precision_per_query = 0
    for iter in range(num_query):
        # 对于一个query label，查看database实际有多少相同的labels Ex: [1,0,0,0,1,1,1,1,0,0]
        ground_truths = (np.dot(query_labels[iter, :], retrieval_labels.transpose()) > 0).astype(np.float32)

        # 对于一个query binary，计算其与其他database里所有的binaries的hamming distance Ex: [2,10,14,9,1,2,1,2,1,4,6]
        hamm_dists = CalcHammingDist(query_binaries[iter, :], retrieval_binaries)

        # 根据从小到的hamming distance，返回对应的index
        hamm_indexes = np.argsort(hamm_dists)

        # 理想情况下: [1,1,1,1,1,0,0,0,0,0]
        # index对应的hamming distance: [1,1,1,2,2,4,6,9,10,14]
        ground_truths = ground_truths[hamm_indexes]

        # topk的选择可能也会有不小的影响。。。
        topK_ground_truths = ground_truths[0:topk]

        # Ex: topK_ground_truths = 5
        topK_ground_truths_sum = np.sum(topK_ground_truths).astype(int)

        # 问题：如果database里面没有query的label咋办。。。？
        if topK_ground_truths_sum == 0:
            # ******需不需要 num_query -= 1
            continue

        # Ex: [1,2,3,4,5]
        matching_binaries = np.linspace(1, topK_ground_truths_sum, topK_ground_truths_sum)

        # ground truths position范围在1 ~ n
        ground_truths_pos = np.asarray(np.where(topK_ground_truths == 1)) + 1.0

        topK_ave_precision_per_query_ = np.mean(matching_binaries / (ground_truths_pos))

        topK_ave_precision_per_query += topK_ave_precision_per_query_

    topK_map = topK_ave_precision_per_query / num_query

    return topK_map


# top_k is hyper-parameter
# Predict label using KNN strategy (a)
def get_labels_pred_KNN(retrieval_binaries, query_binaries, retrieval_labels, query_labels, top_k):
    num_query = query_labels.shape[0]
    labels_pred = []
    for iter in range(num_query):
        hamm_dists = CalcHammingDist(query_binaries[iter, :], retrieval_binaries)

        hamm_indexes = np.argsort(hamm_dists)

        retrieval_labels_sort = retrieval_labels[hamm_indexes]

        topK_retrieval_sorted_labels = retrieval_labels_sort[0:top_k]

        # print("topK_retrieval_sorted_labels: ", topK_retrieval_sorted_labels)

        most_frequent_label = find_most_common_label(topK_retrieval_sorted_labels)

        labels_pred.append(most_frequent_label)

    return labels_pred


# Predict label using Closest Hash Center strategy (b)
def get_labels_pred_closest_hash_center(query_binaries, query_labels, hash_centers):
    num_query = query_labels.shape[0]
    labels_pred = []
    for binary_query, label_query in zip(query_binaries, query_labels):
        dists = CalcHammingDist(binary_query, hash_centers)
        closest_class = np.argmin(dists)
        labels_pred.append(closest_class)
    return labels_pred


# 简单比较query和pred labels的相同个数并算一个accuracy
def compute_labeling_strategy_accuracy(labels_pred, labels_query):
    same = 0

    for i in range(len(labels_pred)):
        if (labels_pred[i] == labels_query[i]).all():
            same += 1

    return same / labels_query.shape[0]


# 计算Binary和得到labels
def compute_result(dataloader, net):
    binariy_codes, labels = [], []
    net.eval()
    for img, label in dataloader:
        labels.append(label)
        binariy_codes.append((net(img.cuda())).data)
    return torch.cat(binariy_codes).sign(), torch.cat(labels)


# 计算hamming distance，B1是一组data，（一个vector），B2是一个matrix（所有database里的vector）
def CalcHammingDist(B1, B2):
    q = B2.shape[1]
    distH = 0.5 * (q - np.dot(B1, B2.transpose()))
    return distH


# 找到重复次数最多的label，还没有考虑怎么break even，或者根据rank来assign不同的weight
def find_most_common_label(labels):
    # 为了hash，变成tuple
    labels_tuple = [tuple(label) for label in labels]

    most_common_label_tuple = Counter(labels_tuple).most_common(1)[0][0]
    return np.array(most_common_label_tuple)


# 把提供的categorical labels转换成one-hot形式
def categorical_to_onehot(labels, numOfClass):
    labels = labels.reshape(labels.shape[0], 1)
    labels = (labels == torch.arange(numOfClass).reshape(1, numOfClass)).int()
    return labels


###------------------------------Model---------------------------------------###
TOP_K = 5

class CSQLightening(pl.LightningModule):
    def __init__(self, n_class, n_features, batch_size=64, l_r=1e-5, lamb_da=0.0001, beta=0.9999, bit=64, lr_decay=0.9, decay_every=20):
        super(CSQLightening, self).__init__()
        print("hparam: l_r = {}, lambda = {}, beta = {}".format(l_r, lamb_da, beta))
        self.batch_size = batch_size
        self.l_r = l_r
        self.bit = bit
        self.n_class = n_class
        self.lamb_da = lamb_da
        self.beta = beta
        self.lr_decay = lr_decay
        self.decay_every = decay_every
        self.samples_in_each_class = None  # Later initialized in training step
        self.hash_centers = get_hash_centers(self.n_class, self.bit)
        ##### model structure ####
        self.hash_layer = nn.Sequential(
            nn.Linear(n_features, 9000),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(9000, 3150),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(3150, 900),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(900, 450),
            nn.ReLU(inplace=True),
            nn.Linear(450, 200),
            nn.ReLU(inplace=True),
            nn.Linear(200, self.bit),
        )

    def forward(self, x):
        # forward pass returns prediction
        x = self.hash_layer(x)
        return x

    def get_class_balance_loss_weight(samples_in_each_class, n_class, beta=0.9999):
        # Class-Balanced Loss on Effective Number of Samples
        # Reference Paper https://arxiv.org/abs/1901.05555
        weight = (1 - beta)/(1 - torch.pow(beta, samples_in_each_class))
        weight = weight / weight.sum() * n_class
        return weight

    def CSQ_loss_function(self, hash_codes, labels):
        hash_codes = hash_codes.tanh()
        hash_centers = self.hash_centers[labels]
        hash_centers = hash_centers.type_as(hash_codes)

        if self.samples_in_each_class == None:
            self.samples_in_each_class = self.trainer.datamodule.samples_in_each_class
            self.n_class = self.trainer.datamodule.N_CLASS

        weight = get_class_balance_loss_weight(
            self.samples_in_each_class, self.n_class, self.beta)
        weight = weight[labels]
        weight = weight.type_as(hash_codes)

        # Center Similarity Loss
        BCELoss = nn.BCELoss(weight=weight.unsqueeze(1).repeat(1, self.bit))
        # BCELoss = nn.BCELoss()
        C_loss = BCELoss(0.5 * (hash_codes + 1),
                         0.5 * (hash_centers + 1))
        # Quantization Loss
        Q_loss = (hash_codes.abs() - 1).pow(2).mean()

        loss = C_loss + self.lamb_da * Q_loss
        return loss

    def training_step(self, train_batch, batch_idx):
        data, labels = train_batch
        hash_codes = self.forward(data)
        loss = self.CSQ_loss_function(hash_codes, labels)

        # 在这里，好像loss本身就会被记录并且显示在progress bar里，
        # 所以"Train_loss_step"我就不在progress bar里显示了，只在tensor board里面显示
        # self.log("Train_loss_step", loss, logger=False)
        return loss

    def validation_step(self, val_batch, batch_idx):
        data, labels = val_batch
        hash_codes = self.forward(data)
        loss = self.CSQ_loss_function(hash_codes, labels)

        return loss

    def validation_epoch_end(self, outputs):

        val_loss_epoch = torch.stack([x for x in outputs]).mean()

        database_dataloader = self.trainer.datamodule.database_dataloader
        val_dataloader = self.trainer.datamodule.val_dataloader()

        val_matrics_CHC = compute_metrics(val_dataloader, self, self.n_class)
        val_labeling_accuracy_CHC, val_F1_score_weighted_average_CHC, val_F1_score_median_CHC, val_F1_score_per_class_CHC = val_matrics_CHC

        if not self.trainer.running_sanity_check:
            print(f"Epoch: {self.current_epoch}, Val_loss_epoch: {val_loss_epoch:.2f}")
            print(f"val_F1_score_median_CHC:{val_F1_score_median_CHC:.3f}, val_labeling_accuracy_CHC:{val_labeling_accuracy_CHC:.3f},\
                   val_F1_score_weighted_average_CHC:{val_F1_score_weighted_average_CHC:.3f},\
                   val_F1_score_per_class_CHC:{[f'{score:.3f}' for score in val_F1_score_per_class_CHC]}")

        value = {"Val_loss_epoch": val_loss_epoch,
                  "Val_F1_score_median_CHC_epoch": val_F1_score_median_CHC,
                  "Val_labeling_accuracy_CHC_epoch": val_labeling_accuracy_CHC,
                  "Val_F1_score_weighted_average_CHC_epoch": val_F1_score_weighted_average_CHC, }
        self.log_dict(value, prog_bar=True, logger=True)

    def test_step(self, test_batch, batch_idx):
        data, labels = test_batch
        hash_codes = self.forward(data)
        loss = self.CSQ_loss_function(hash_codes, labels)

        return loss

    def test_epoch_end(self, outputs):
        test_loss_epoch = torch.stack([x for x in outputs]).mean()

        database_dataloader = self.trainer.datamodule.database_dataloader
        test_dataloader = self.trainer.datamodule.test_dataloader()

        test_matrics_CHC = compute_metrics(test_dataloader, self, self.n_class, show_time=True, use_cpu=True)
        test_labeling_accuracy_CHC, test_F1_score_weighted_average_CHC, test_F1_score_median_CHC, test_F1_score_per_class_CHC = test_matrics_CHC

        if not self.trainer.running_sanity_check:
            print(f"Epoch: {self.current_epoch}, Test_loss_epoch: {test_loss_epoch:.2f}")
            print(f"test_F1_score_median_CHC:{test_F1_score_median_CHC:.3f}, test_labeling_accuracy_CHC:{test_labeling_accuracy_CHC:.3f}, \
                    test_F1_score_weighted_average_CHC:{test_F1_score_weighted_average_CHC:.3f}, \
                    test_F1_score_per_class_CHC:{[f'{score:.3f}' for score in test_F1_score_per_class_CHC]}")

        value = {"Test_loss_epoch": test_loss_epoch,
                 "Test_F1_score_median_CHC_epoch": test_F1_score_median_CHC,
                 "Test_labeling_accuracy_CHC_epoch": test_labeling_accuracy_CHC,
                 "Test_F1_score_weighted_average_CHC_epoch": test_F1_score_weighted_average_CHC}
        self.log_dict(value, prog_bar=True, logger=True)

    def configure_optimizers(self):
        # optimizer = torch.optim.RMSprop(self.parameters(),
        #                                 lr=self.l_r, weight_decay=10**-4)
        optimizer = torch.optim.Adam(self.parameters(),
                                     lr=self.l_r, weight_decay=10**-5)

        # Decay LR by a factor of gamma every step_size epochs
        exp_lr_scheduler = lr_scheduler.StepLR(
            optimizer, step_size=self.decay_every, gamma=self.lr_decay)

        return [optimizer], [exp_lr_scheduler]
