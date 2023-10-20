from utils import read_logs, read_models, split_list, get_all_ready_logs, read_log, split_data
from filehelper import gather_all_xes, get_all_ready_logs
from features import read_feature_matrix, read_feature_vector, feature_no_total_traces
from measures import read_target_entry, read_target_entries
from init import *
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from filehelper import gather_all_xes, select_smallest_k_logs
import multiprocessing
import globals
import numpy as np
import os
import pm4py
import sys
project_dir = '/rwthfs/rz/cluster/home/qc261227/Recommender/RecommenderSystem/backend/src'
# Add the project directory to sys.path
sys.path.append(project_dir)

label_to_index = {label: index for index,
                  label in enumerate(globals.algorithm_portfolio)}


all_labels = list(label_to_index.keys())

classification_methods = ["decision_tree", "knn", "svm",
                          "random_forest", "logistic_regression", "gradient_boosting"]


def classification(log_path, X, y, classification_method):
    if classification_method == "decision_tree":
        clf = DecisionTreeClassifier()
    elif classification_method == "knn":
        clf = KNeighborsClassifier()
    elif classification_method == "svm":
        clf = SVC(probability=True)
    elif classification_method == "random_forest":
        clf = RandomForestClassifier()
    elif classification_method == "logistic_regression":
        clf = LogisticRegression()
    elif classification_method == "gradient_boosting":
        clf = GradientBoostingClassifier()
    else:
        raise ValueError(
            f"Invalid classification method: {classification_method}")

    clf = clf.fit(X, y)

    # Calculate probabilities for all labels
    probabilities = clf.predict_proba(read_feature_vector(log_path))

    label_probabilities = {label: probability for label, probability in zip(
        all_labels, probabilities[0])}

    for label in globals.algorithm_portfolio:
        if label not in label_probabilities:
            label_probabilities[label] = 0

    return label_probabilities


if __name__ == "__main__":

    selected_measures = ["node_arc_degree", "no_total_elements",
                         "used_memory", "pm4py_simplicity", "runtime"]

    measure_name = "runtime"

    training = get_all_ready_logs(
        gather_all_xes("../logs/training"), "runtime")
    testing = get_all_ready_logs(
        gather_all_xes("../logs/testing"), "runtime")[:10]

    x_train = read_feature_matrix(training)
    y_train = read_target_vector(training, measure_name)

    for classification_method in classification_methods:
        print(classification(testing[0], x_train,
              y_train, classification_method))
