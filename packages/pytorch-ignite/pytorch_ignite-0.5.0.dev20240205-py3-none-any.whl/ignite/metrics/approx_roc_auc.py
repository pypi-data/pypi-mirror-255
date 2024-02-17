import numbers
from typing import Callable, Optional, Sequence, Tuple, Union

import torch

from ignite.metrics.confusion_matrix import _BaseConfusionMatrix
from ignite.metrics.metric import reinit__is_reduced, sync_all_reduce
from ignite.metrics.metrics_lambda import MetricsLambda


class BinaryThresholdConfusionMatrix(_BaseConfusionMatrix):
    """
    Implements a confusion matrix over a set of thresholds (inclusive) with GPU support
    Leverage redundant computations for monotonically increasing thresholds
    Accumulate confusion in running count tensor for all thresholds (T,4)
    Supports MetricLambdas to reuse confusion matrix statistics across thresholds
    - Accuracy         ~ returns Tensor with dim (T,)
    - Precision        ~ returns Tensor with dim (T,)
    - Recall           ~ returns Tensor with dim (T,)
    - Specificity      ~ returns Tensor with dim (T,)
    - PrecisionRecall  ~ returns (Precision, Recall)
    - F1               ~ returns Tensor with dim (T,)
    - BalancedAccuracy ~ returns Tensor with dim (T,)
    - MCC              ~ returns Tensor with dim (T,)

    NOTE:
        Metric should not be directly attached to an engine - please attach lambdas instead as needed
        Assumes all tensors have been detached from computational graph - see .detach()
        some elements of the confusion matrix may be zero and may exhibit
        unexpected behavior. Please monitor experiments as needed
    """

    def __init__(
        self,
        thresholds: torch.Tensor,
        average: Optional[str] = None,
        output_transform: Callable = lambda x: x,
        device: Union[str, torch.device] = torch.device("cpu")
    ):
        self.thresholds = thresholds
        # super's init should come last since Metric overrides __getattr__ and that messes with self.<foo>'s behavior
        super().__init__(average=average, output_transform=output_transform, device=device)

    @reinit__is_reduced
    def reset(self) -> None:
        self.confusion_matrix = torch.zeros(4, len(self.thresholds), dtype=torch.int64, device=self._device)
        super(BinaryThresholdConfusionMatrix, self).reset()

    @reinit__is_reduced
    def update(self, output: Sequence[torch.Tensor]) -> None:
        preds, labels = output[0].detach(), output[1].detach()
        # if preds.device != self.device: preds = preds.to(self.device)                     # coord device
        # if labels.device != self.device: labels = labels.to(self.device)                  # coord device
        preds, labels = preds.view(-1), labels.view(-1)                                   # flatten
        preds, locs = torch.sort(preds)                                                   # sort
        labels = torch.cumsum(labels[locs], 0)                                            # pool for reuse
        labels = torch.cat([torch.tensor([0], device=self.device), labels], dim=0)        # pre-pending 0
        changes = torch.searchsorted(preds, self.thresholds, right=True)                  # get threshold change index
        neg_preds = labels[changes]                                                       # get fwd change accumulation
        pos_preds = labels[-1] - neg_preds                                                # get bck change accumulation
        self.confusion_matrix[0] += (pos_preds).to(self._device, dtype=torch.long)                          # TP
        self.confusion_matrix[1] += (len(labels)-1-changes-pos_preds).type(torch.long)    # FP (-1 accounts for prepend. 0)
        self.confusion_matrix[2] += (changes - neg_preds).type(torch.long)                # TN
        self.confusion_matrix[3] += (neg_preds).type(torch.long)                          # FN

    @sync_all_reduce("confusion_matrix")
    def compute(self) -> torch.Tensor:
        return super(BinaryThresholdConfusionMatrix, self).compute()


def btcmAccuracy(cm: BinaryThresholdConfusionMatrix, reduce=True) -> MetricsLambda:
    """
        Accuracy = (TP + TN) / (TP + FP + TN + FN)
    """
    cm = cm.type(torch.DoubleTensor)
    accuracy = (cm[0]+cm[2]) / (cm.sum(dim=0) + 1e-15)
    return accuracy.max() if reduce else accuracy

def btcmPrecision(cm: BinaryThresholdConfusionMatrix, reduce=True) -> MetricsLambda:
    """
        Precision = PPV = 1 - FDR = TP / (TP + FP)
    """
    cm = cm.type(torch.DoubleTensor)
    precision = cm[0] / (cm[0]+cm[1] + 1e-15)
    return precision.max() if reduce else precision

def btcmRecall(cm: BinaryThresholdConfusionMatrix, reduce=True) -> MetricsLambda:
    """
        Recall = Sensitivity = TPR = 1 - FNR = TP / (TP + FN)
    """
    cm = cm.type(torch.DoubleTensor)
    recall = cm[0] / (cm[0]+cm[3] + 1e-15)
    return recall.max() if reduce else recall

def btcmSpecificity(cm: BinaryThresholdConfusionMatrix, reduce=True) -> MetricsLambda:
    """
        Specificity = TNR = 1 - FPR = TN / (TN + FP)
    """
    cm = cm.type(torch.DoubleTensor)
    specificity = cm[2] / (cm[2]+cm[1] + 1e-15)
    return specificity.max() if reduce else specificity

def btcmPrecisionRecall(cm: BinaryThresholdConfusionMatrix) -> MetricsLambda:
    precision_recall = (btcmPrecision(cm, False), btcmRecall(cm, False))
    return precision_recall

def btcmF1(cm: BinaryThresholdConfusionMatrix, reduce=True) -> MetricsLambda:
    """
        F1 = Dice = harmonic mean of precision and recall = 2*TP / (2*TP + FP + FN)
    """
    precision, recall = btcmPrecisionRecall(cm)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-15)
    return f1.max() if reduce else f1

def btcmBalancedAccuracy(cm: BinaryThresholdConfusionMatrix, reduce=True) -> MetricsLambda:
    """
        Balanced Accuracy = (TPR + TNR) / 2
    """
    recall, specificity = (btcmRecall(cm, False), btcmSpecificity(cm, False))
    ba = (recall + specificity) / 2
    return ba.max() if reduce else ba

def btcmMCC(cm: BinaryThresholdConfusionMatrix, reduce=True) -> MetricsLambda:
    """
        Matthews correlation coefficient = phi coefficient
    """
    cm = cm.type(torch.DoubleTensor)
    # TP = cm[0], FP = cm[1], TN = cm[2], FN = cm[3]
    mcc = (cm[0]*cm[2] - cm[1]*cm[3]) / (((cm[0]+cm[1])*(cm[0]+cm[3])*(cm[2]+cm[1])*(cm[2]+cm[3]))**0.5 + 1e-15)
    return mcc.max() if reduce else mcc

class ApproximateMetrics():
    '''
        This class can be used to approximate ROC type statistics via preset thresholds
        It should be known that this method may under/over estimate true AUCs depending on T
        - ApproxPR_AUC      ~ returns float of Precision-Recall AUC over T
        - ApproxROC_AUC     ~ returns float of ROC AUC over T (worst case, under-estimated)
    '''

    @staticmethod
    def ApproxPR_AUC(cm:BinaryThresholdConfusionMatrix) -> MetricsLambda:
        precision, recall = btcmPrecisionRecall(cm)
        auc = -1 * MetricsLambda(torch.trapz, precision, recall)
        return auc

    @staticmethod
    def ApproxROC_AUC(cm:BinaryThresholdConfusionMatrix) -> MetricsLambda:
        tpr = btcmRecall(cm, False)
        fpr = cm[1] / (cm[1] + cm[2] + 1e-15)
        auc = -1 * MetricsLambda(torch.trapz, tpr, fpr)
        return auc