import pm4py
import sys
import math
import globals
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from utils import read_model, read_log
from utils import generate_cache_file, generate_log_id, store_cache_variable, load_cache_variable, compute_model
from filehelper import gather_all_xes, split_file_path, get_all_ready_logs


def measure_token_fitness(log_path, discovery_algorithm):
    log = read_log(log_path)
    petri_net, initial_marking, final_marking = read_model(
        log_path, discovery_algorithm)
    result = pm4py.conformance.fitness_token_based_replay(
        log, petri_net, initial_marking, final_marking)
    print(discovery_algorithm, result["average_trace_fitness"])
    return result["average_trace_fitness"]


def measure_alignment_fitness(log_path, discovery_algorithm):
    log = read_log(log_path)
    petri_net, initial_marking, final_marking = read_model(
        log_path, discovery_algorithm)
    result = pm4py.conformance.fitness_alignments(
        log, petri_net, initial_marking, final_marking)
    print(discovery_algorithm, result["average_trace_fitness"])
    return result["average_trace_fitness"]

# PRECISION


def measure_token_precision(log_path, discovery_algorithm):
    log = read_log(log_path)
    petri_net, initial_marking, final_marking = read_model(
        log_path, discovery_algorithm)
    result = pm4py.conformance.precision_token_based_replay(
        log, petri_net, initial_marking, final_marking)
    print(discovery_algorithm, result)
    return result


def measure_alignment_precision(log_path, discovery_algorithm):
    log = read_log(log_path)
    petri_net, initial_marking, final_marking = read_model(
        log_path, discovery_algorithm)
    result = pm4py.conformance.precision_alignments(
        log, petri_net, initial_marking, final_marking)
    print(discovery_algorithm, result)
    return result


def number_of_places(net):
    return len(net._PetriNet__places)


def number_of_transitions(net):
    return len(net._PetriNet__transitions)


def number_of_arcs(net):
    return len(net._PetriNet__arcs)

# SIMPLICITY MEAURES


def measure_no_total_elements(log_path, discovery_algorithm):
    """Takes in net only as input
    Args:
        net: net, as returned by a discovery algorithm
    """
    net, _, _ = read_model(log_path, discovery_algorithm)
    return number_of_arcs(net) + number_of_places(net) + number_of_transitions(net)


def measure_node_arc_degree(log_path, discovery_algorithm):
    net, _, _ = read_model(log_path, discovery_algorithm)
    return number_of_arcs(net) / (number_of_transitions(net) + number_of_places(net))


# performance measures
def measure_runtime(log_path, discovery_algorithm):
    log_id = generate_log_id(log_path)
    runtime_cache_file = f"{globals.flask_app_path}/cache/measures/{discovery_algorithm}_runtime_{log_id}.pkl"
    read_model(log_path, discovery_algorithm)
    try:
        runtime = load_cache_variable(runtime_cache_file)
    except Exception as e:
        print(e)
        print("Runtime somehow couldn't be computed")

    return runtime


def measure_used_memory(log_path, discovery_algorithm):
    model = read_model(log_path, discovery_algorithm)
    return sys.getsizeof(model)


def measure_generalization(log_path, discovery_algorithm):
    net, im, fm = read_model(log_path, discovery_algorithm)
    log = read_log(log_path)
    return generalization_evaluator.apply(log, net, im, fm)


def measure_pm4py_simplicity(log_path, discovery_algorithm):
    net, im, fm = read_model(log_path, discovery_algorithm)
    log = read_log(log_path)
    return simplicity_evaluator.apply(net)


def measure_log_runtime(log_path, discovery_algorithm):
    log_id = generate_log_id(log_path)
    runtime_cache_file = f"{globals.flask_app_path}/measures/{discovery_algorithm}_log_runtime_{log_id}.pkl"
    read_model(log_path, discovery_algorithm)
    try:
        runtime = load_cache_variable(runtime_cache_file)
    except Exception as e:
        print(e)
        print("Runtime somehow couldn't be computed")

    return runtime


def compute_measure(log_path, discovery_algorithm, measure_name):
    if measure_name == "token_fitness":
        return measure_token_fitness(log_path, discovery_algorithm)
    elif measure_name == "alignment_fitness":
        return measure_alignment_fitness(log_path, discovery_algorithm)
    elif measure_name == "token_precision":
        return measure_token_precision(log_path, discovery_algorithm)
    elif measure_name == "alignment_precision":
        return measure_alignment_precision(log_path, discovery_algorithm)
    elif measure_name == "no_total_elements":
        return measure_no_total_elements(log_path, discovery_algorithm)
    elif measure_name == "node_arc_degree":
        return measure_node_arc_degree(log_path, discovery_algorithm)
    elif measure_name == "runtime":
        return measure_runtime(log_path, discovery_algorithm)
    elif measure_name == "used_memory":
        return measure_used_memory(log_path, discovery_algorithm)
    elif measure_name == "generalization":
        return measure_generalization(log_path, discovery_algorithm)
    elif measure_name == "pm4py_simplicity":
        return measure_pm4py_simplicity(log_path, discovery_algorithm)
    else:
        raise ValueError("Invalid measure name")


def read_max_target_vector(log_path,  measure_name, algorithm_portfolio):
    cur_max = float("-inf")
    cur_algo = None
    for discovery_algorithm in algorithm_portfolio:
        algo_val = read_measure_entry(
            log_path, discovery_algorithm, measure_name)
        if algo_val > cur_max:
            cur_max = algo_val
            cur_algo = discovery_algorithm

    return cur_algo


def read_min_target_vector(log_path, measure_name, algorithm_portfolio):
    cur_min = float("inf")
    cur_algo = None
    for discovery_algorithm in algorithm_portfolio:
        algo_val = read_measure_entry(
            log_path, discovery_algorithm, measure_name)
        if algo_val < cur_min:
            cur_min = algo_val
            cur_algo = discovery_algorithm

    return cur_algo


def read_measure_entry(log_path, discovery_algorithm, measure_name):

    if (log_path, discovery_algorithm, measure_name) in globals.measures:
        return globals.measures[log_path, discovery_algorithm, measure_name]

    log_id = generate_log_id(log_path)
    cache_file_path = generate_cache_file(
        f"{globals.flask_app_path}/cache/measures/{discovery_algorithm}_{measure_name}_{log_id}.pkl")
    try:
        measure_entry = load_cache_variable(cache_file_path)
    except Exception:
        print("No cached measure entry found, now computing measure")
        measure_entry = compute_measure(
            log_path, discovery_algorithm, measure_name)
        store_cache_variable(measure_entry, cache_file_path)
    return measure_entry


def read_target_entry(log_path, measure_name, algorithm_portfolio):
    if globals.measures_kind[measure_name] == "max":
        target_entry = read_max_target_vector(
            log_path, measure_name, algorithm_portfolio)
        return target_entry
    if globals.measures_kind[measure_name] == "min":
        target_entry = read_min_target_vector(log_path, measure_name, algorithm_portfolio
                                              )
        return target_entry

    return None


def read_target_entries(log_paths, measure_name):
    for log_path in log_paths:
        try:
            read_target_entry(log_path, measure_name)
        except Exception as e:
            print(f"Sorry couldn't compute certain measure:{measure_name}")
            print(e)


def read_classification_target_vector(log_paths, measure_name, algorithm_portfolio):
    n = len(log_paths)
    y = [None]*n

    for i in range(n):
        y[i] = read_target_entry(
            log_paths[i], measure_name, algorithm_portfolio)
    return y


def read_regression_target_vector(log_paths, discovery_algorithm, measure_name):
    n = len(log_paths)
    y = [None]*n

    for i in range(n):
        y[i] = read_measure_entry(
            log_paths[i], discovery_algorithm, measure_name)
    return y


def read_binary_classification_target_entry(log_path, measure_name, algorithm_a, algorithm_b):
    return read_target_entry(log_path, measure_name, [
        algorithm_a, algorithm_b])


def read_binary_classification_target_vector(log_paths, measure_name, algorithm_a, algorithm_b):
    n = len(log_paths)
    y = [None]*n

    for i in range(n):
        y[i] = read_binary_classification_target_entry(
            log_paths[i], measure_name, algorithm_a, algorithm_b)
    return y


if __name__ == "__main__":
    log_paths = get_all_ready_logs(gather_all_xes(
        "../logs/training") + gather_all_xes("../logs/testing"), "runtime")

    for log_path in log_paths:
        for discovery_algorithm in globals.algorithm_portfolio:
            log_name = split_file_path(log_path)["filename"]
            current_runtime = read_measure_entry(
                log_path, discovery_algorithm, "log_runtime")
            # store_cache_variable(math.log10(current_runtime),f"./cache/measures/{discovery_algorithm}_log_runtime_{log_name}.pkl")
