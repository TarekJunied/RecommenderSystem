import os
import glob
import numpy as np
import warnings
import math
import globals
import time
import pm4py
import sys
from flask_app.init import init_log
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from flask_app.utils import read_log, generate_log_id, generate_cache_file, store_cache_variable, load_cache_variable, get_log_name, read_model, split_file_path
from flask_app.features.removed_features import get_removed_features_list
from flask_app.features.fig4pm_features.fig4pm_interface import get_fig4pm_feature_functions_dict
from flask_app.features.own_features import get_own_features_dict
from flask_app.features.mtl_features.mtl_feature_interface import get_mtl_feature_functions_dict
from flask_app.filehelper import gather_all_xes, get_all_ready_logs
from flask_app.feature_controller import read_single_feature
from flask_app.evaluation import mo_min_max_single_point_accuracy
from flask_app.multiobjective import predicted_regression_based_scalarization, actual_regression_based_scalarization
from flask_app.measures import read_measure_entry
# Version: 2.7.8.4


def is_sublist(list1, list2):
    """Check if list1 is a sublist of list2."""
    # If list1 is longer, it can't be a sublist
    if len(list1) > len(list2):
        return False

    # Loop over list2
    for i in range(len(list2) - len(list1) + 1):
        # Check if the slice of list2 equals list1
        if list2[i:i+len(list1)] == list1:
            return True

    return False


def log_log_collection_info(log_paths):

    cases = [read_single_feature(log_path, "n_traces")
             for log_path in log_paths]
    events = [read_single_feature(log_path, "n_events")
              for log_path in log_paths]
    activities = [read_single_feature(
        log_path, "n_unique_activities") for log_path in log_paths]
    trace_len_min = [read_single_feature(
        log_path, "trace_len_min") for log_path in log_paths]
    trace_len_max = [read_single_feature(
        log_path, "trace_len_max") for log_path in log_paths]
    n_unique_traces = [read_single_feature(
        log_path, "n_unique_traces") for log_path in log_paths]

    print("#logs", len(log_paths))
    print(f"#cases: {min(cases)} -{max(cases)}")
    print(f"#events: {min(events)} -{max(events)}")
    print(f"#activities: {min(activities)} -{max(activities)}")
    print(f"trace: {max(trace_len_min)} -{min(trace_len_max)}")
    print(f"#variants {min(n_unique_traces)} - {max(n_unique_traces)}")


def mo_min_max_single_point_accuracy(actual_dict, predicted_dict):

    best_actual_algo = max(actual_dict, key=actual_dict.get)
    worst_actual_algo = min(actual_dict, key=actual_dict.get)

    best_predicted_algo = max(predicted_dict, key=predicted_dict.get)

    if best_predicted_algo == worst_actual_algo:
        accuracy = 0
    else:
        # Using min-max normalization to calculate accuracy
        predicted_value = predicted_dict[best_predicted_algo]
        worst_value = actual_dict[worst_actual_algo]
        best_value = actual_dict[best_actual_algo]

        # Ensure the denominator is not zero
        if best_value != worst_value:
            accuracy = (predicted_value - worst_value) / \
                (best_value - worst_value)
            # Ensuring accuracy is between 0 and 1
            accuracy = max(0, min(accuracy, 1))
        else:
            # If the worst and best actual performance are the same, can't compute as usual
            accuracy = 0  # or some other rule as defined by system requirements

    return accuracy


if __name__ == "__main__":
    all_logs = gather_all_xes("../logs/real_life_logs")

    measure_weights_dict_list = [
        # Checking each dictionary for exactly two measures with a value of 1
        {"token_fitness": 1, "token_precision": 1,
            "pm4py_simplicity": 0, "generalization": 0},
        {"token_fitness": 1, "token_precision": 0,
            "pm4py_simplicity": 1, "generalization": 0},
        {"token_fitness": 1, "token_precision": 0,
            "pm4py_simplicity": 0, "generalization": 1},
        {"token_fitness": 0, "token_precision": 1,
            "pm4py_simplicity": 1, "generalization": 0},
        {"token_fitness": 0, "token_precision": 1,
            "pm4py_simplicity": 0, "generalization": 1},
        {"token_fitness": 0, "token_precision": 0,
            "pm4py_simplicity": 1, "generalization": 1},
    ]

    chosen_log_name = "Road_Traffic_Fine_Management_Process"

    all_ready_logs = get_all_ready_logs(
        all_logs, globals.feature_portfolio, globals.algorithm_portfolio, globals.measure_portfolio)

    correctly_predicted_logs = []
    for log_path in all_ready_logs:
        for measure_weights_dict in measure_weights_dict_list:
            if get_log_name(log_path) == chosen_log_name:
                all_ready_logs = [log_path]
                predicted_scores_dict = predicted_regression_based_scalarization(
                    log_path, "xgboost", measure_weights_dict, [], globals.feature_portfolio, globals.algorithm_portfolio)
                actual_scores_dict = actual_regression_based_scalarization(
                    log_path, measure_weights_dict, globals.algorithm_portfolio)
                predicted_accuracy = mo_min_max_single_point_accuracy(
                    actual_scores_dict, predicted_scores_dict)
                input([m for m in measure_weights_dict if measure_weights_dict[m] > 0])
                input(max(predicted_scores_dict, key=predicted_scores_dict.get))
                input(max(actual_scores_dict, key=actual_scores_dict.get))

    discs = {}
    for log_path in all_ready_logs:

        for discovery_algorithm in globals.algorithm_portfolio:
            net, im, fm = read_model(log_path, discovery_algorithm)
            log_name = get_log_name(log_path)
            parameters = {"format": "png"}
            gviz = pn_visualizer.apply(net, im, fm, parameters=parameters)
            pn_visualizer.save(
                gviz, f"./INTRODUCTION/{discovery_algorithm}_{log_name}.png")
            discs[discovery_algorithm] = {measure: read_measure_entry(log_path, discovery_algorithm, measure)
                                          for measure in globals.measure_portfolio}
