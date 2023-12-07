import sys
import psutil
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import numpy as np
import globals
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from utils import get_all_ready_logs,load_cache_variable
from recommender import classification
from filehelper import gather_all_xes, get_all_ready_logs_multiple,split_file_path
from measures import read_target_entries, read_target_entry, read_target_vector,  read_worst_entry,read_measure_entry
from features import read_feature_matrix
from init import init

def get_number_one(input_dict):
    for key, value in input_dict.items():
        if value == 1:
            return key
    return None  # Return None if no key with value 1 is found


def create_scikit_evaluation_plot(selected_measures, classification_method="knn"):
    values = []
    categories = selected_measures
    display_str = ""

    ready_testing  = list(globals.testing_log_paths.keys())


    for measure in selected_measures:
    
        display_str += f" {len(ready_testing)} "
        values += [evaluate_scikit_measure_accuracy(measure,classification_method)]




    plt.figure(figsize=(8, 6))  # Adjust the figure size if needed
    plt.bar(categories, values, color='royalblue')
    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.title(display_str)

    # Set y-axis ticks and limits
    plt.yticks([i/10 for i in range(11)])
    plt.ylim(0, 1)

    for i in range(1, 10):
        plt.axhline(y=i/10, color='gray', linestyle='--', linewidth=0.5)

    plt.grid(True, axis='y', linestyle='--', alpha=0.7)  # Add a horizontal grid
    plt.xticks(rotation=90)

    now = datetime.now()

    # Format the current date as a string
    current_date_string = now.strftime("%Y-%m-%d")

    if not os.path.exists(f"../evaluation/scikit_{current_date_string}"):
    # If it doesn't exist, create the directory
        os.mkdir(f"../evaluation/scikit_{current_date_string}")

    plt.savefig(f'../evaluation/scikit_{current_date_string}/{classification_method}_accuracy_{int(time.time())}.png', dpi=300, bbox_inches='tight')



def evaluate_scikit_measure_accuracy(measure,classification_method):

    ready_testing = list(globals.testing_log_paths.keys())

    y_true = [None] * len(ready_testing)
    y_pred = [None] * len(ready_testing)

    for i in range(len(ready_testing)):
        y_true[i] = read_target_entry(ready_testing[i], measure)
        y_pred[i] = classification(ready_testing[i],  classification_method,measure)


    return accuracy_score(y_true, y_pred)

def create_min_max_evaluation_plot(selected_measures, classification_method="knn"):
    values = []
    categories = selected_measures
    display_str = ""
    ready_training = list(globals.training_log_paths.keys())
    ready_testing  = list(globals.testing_log_paths.keys())
    for measure in selected_measures:
        

        display_str += f" {len(ready_testing)} "
        values += [evaluate_min_max_measure_accuracy(ready_testing,measure,classification_method)]


    plt.figure(figsize=(8, 6))  # Adjust the figure size if needed
    plt.bar(categories, values, color='royalblue')
    plt.xlabel('Categories')
    plt.ylabel('Values')
    plt.title(display_str)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)  # Add a horizontal grid
    plt.xticks(rotation=90)
    
    now = datetime.now()

    # Format the current date as a string
    current_date_string = now.strftime("%Y-%m-%d")

    if not os.path.exists(f"../evaluation/min_max_{current_date_string}"):

        os.mkdir(f"../evaluation/min_max_{current_date_string}")

    plt.savefig(f'../evaluation/min_max_{current_date_string}/{classification_method}_accuracy_{int(time.time())}.png', dpi=300, bbox_inches='tight')



def evaluate_min_max_measure_accuracy(testing_log_paths, measure_name, classification_method="knn"):

    if measure_name not in globals.normalisierbare_measures:
        print("Can't evaluate accuracy for this measure")
        return False

    
    y_best = [None]*(len(testing_log_paths))
    y_worst = [None]*(len(testing_log_paths))
    y_pred = [None]*(len(testing_log_paths))

  
    sum = 0

    for i in range(len(testing_log_paths)):

        y_best[i] = read_target_entry(
            testing_log_paths[i], measure_name)
        y_worst[i] =  read_worst_entry(testing_log_paths[i], measure_name)
        y_pred[i] = get_number_one(classification(
            testing_log_paths[i],classification_method,measure_name)[1])

        cur_name_log = split_file_path(testing_log_paths[i])["filename"]

        cur_max_val = load_cache_variable(f"./cache/measures/{y_best[i]}_{measure_name}_{cur_name_log}.pkl")
        cur_min_val = load_cache_variable(f"./cache/measures/{y_worst[i]}_{measure_name}_{cur_name_log}.pkl")
        if y_best[i] == y_worst[i]:
            print("wtf") 
        cur_pred_val = load_cache_variable(f"./cache/measures/{y_pred[i]}_{measure_name}_{cur_name_log}.pkl")

        if cur_max_val == cur_min_val:
            cur_min_max = 1
        else:
            cur_min_max = (cur_pred_val - cur_min_val) / (cur_max_val - cur_min_val)


        sum += cur_min_max
      
    return sum / len(testing_log_paths)


def create_two_measure_graph(measure_name1,measure_name2,discovery_algorithm):
    original_logpaths = gather_all_xes("../logs/training") + gather_all_xes("../logs/testing")
    full_logs = set(get_all_ready_logs(original_logpaths,measure_name1
                                  )).intersection(set(get_all_ready_logs(original_logpaths,measure_name2)))
    
    full_logs = list(full_logs)
    x_values = []
    y_values = []

    for log_path in full_logs:
            x_values +=[read_measure_entry(log_path,discovery_algorithm,measure_name1)]
            y_values +=[read_measure_entry(log_path,discovery_algorithm,measure_name2)]

    # Plotting the points
    plt.scatter(x_values, y_values, color='red', label='Points', s=2)

    # Adding labels and title
    plt.xlabel(measure_name1)
    plt.ylabel(measure_name2)
    plt.title(f"{measure_name1} vs {measure_name2} with {discovery_algorithm} and {len(x_values)} values")

    # Display the legend
    plt.xlim(0, 1)
    plt.ylim(0, 1)


    now = datetime.now()

    current_date_string = now.strftime("%Y-%m-%d")

    if not os.path.exists(f"../evaluation/measure_comparisons_{current_date_string}"):
    # If it doesn't exist, create the directory
        os.mkdir(f"../evaluation/measure_comparisons_{current_date_string}")

    plt.savefig(f"../evaluation/measure_comparisons_{current_date_string}/{discovery_algorithm}_{measure_name1}_{measure_name2}_{int(time.time())}.png", dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    sys.setrecursionlimit(5000)


    measures_list = ["token_fitness",  "token_precision",
                              "generalization", "pm4py_simplicity"]

    for i in range(len(measures_list)):
        for j in range(i+1, len(measures_list)):
                measure_name1 = measures_list[i]
                measure_name2 = measures_list[j]
                for discovery_algorithm in globals.algorithm_portfolio:
                    create_two_measure_graph(measure_name1,measure_name2,discovery_algorithm)


