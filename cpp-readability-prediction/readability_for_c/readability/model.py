from sklearn import metrics


class Model:
    def __init__(self, pipeline, target, predicted, cutoff, available_features, selected_features):
        self.pipeline = pipeline
        self.target = target
        self.predicted = predicted
        self.cutoff = cutoff
        self.available_features = available_features
        self.selected_features = selected_features

        self.auc = metrics.roc_auc_score(y_true=target, y_score=predicted)
        self.cm = metrics.confusion_matrix(target, predicted)
        self.accuracy = metrics.accuracy_score(target, predicted)

    def __str__(self):
        selected_features_len = self.available_features if self.selected_features is None else len(self.selected_features)
        return " ".join(["Model statistics: \n",
                         "AUC score: ", str(round(self.auc, 2)), "\n",
                         "Confusion matrix: \n", str(self.cm), "\n",
                         "Accuracy: ", str(round(self.accuracy, 2)), "\n",
                         str(selected_features_len), " selected features, namely: \n",
                         str(self.selected_features), "\n"
                         ])
