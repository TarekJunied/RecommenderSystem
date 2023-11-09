home_dir = "/Users/tarekjunied/Documents/Universität/BachelorThesis"
algorithm_portfolio = ["alpha", "heuristic",
                       "inductive", "ILP", "split"]
features_list = ["no_distinct_traces", "no_total_traces", "avg_trace_length", "avg_event_repetition_intra_trace",
                 "no_distinct_events", "no_events_total", "no_distinct_start", "no_distinct_end", "causality_strength", "density", "length_one_loops"]

selected_features = ["no_distinct_traces", "no_total_traces", "avg_trace_length", "avg_event_repetition_intra_trace",
                     "no_distinct_events", "no_events_total", "no_distinct_start", "no_distinct_end", "density", "length_one_loops"]


measures = {"token_fitness": "max", "alignment_fitness": "max", "token_precision": "max",
            "alignment_precision": "max", "no_total_elements": "min", "node_arc_degree": "min", "runtime": "min", "used_memory": "min", "generalization": "max", "pm4py_simplicity": "max"}

measures_list = ["token_fitness", "alignment_fitness", "token_precision", "alignment_precision",
                 "no_total_elements", "node_arc_degree", "runtime", "used_memory", "generalization", "pm4py_simplicity"]

normalisierbare_measures = {"token_fitness": "max", "alignment_fitness": "max", "token_precision": "max",
                            "alignment_precision": "max",  "generalization": "max", "pm4py_simplicity": "max"}


classification_methods = ["decision_tree", "knn", "svm",
                          "random_forest", "logistic_regression", "gradient_boosting"]

selected_measure = "token_precision"
working_dir = "/Users/tarekjunied/Documents/Universität/BachelorThesis"
models = {}
training_logs_paths = []
feature_vectors = {}
logs = {}
pickled_variables = {}
target_vectors = {}
runtime = {}
y = None

X = None

no_logs = 4
