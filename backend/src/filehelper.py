import os
import globals


def gather_all_xes(dir_path):
    xes_files = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".xes"):
                xes_files.append(os.path.join(root, file))

    return xes_files


def select_smallest_k_logs(k, dir_path):
    # Create a list of tuples containing (file_path, file_size)
    globals.training_logs_paths = gather_all_xes(dir_path)
    files_with_sizes = [(file_path, os.path.getsize(file_path))
                        for file_path in globals.training_logs_paths]

    # Sort the list of tuples by file size
    sorted_files = sorted(files_with_sizes, key=lambda x: x[1])

    # Extract the sorted file paths from the sorted list of tuples
    sorted_file_paths = [file_path for file_path, _ in sorted_files]

    return sorted_file_paths[:k]


def remove_extension(filename):
    base = os.path.basename(filename)  # Get the filename without path
    name_without_extension = os.path.splitext(base)[0]  # Remove the extension
    return name_without_extension