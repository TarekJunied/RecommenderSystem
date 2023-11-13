import subprocess
import datetime
import math
import sys
import os
import shutil
import random
import multiprocessing
import hashlib
# TODO remove relative paths and perhaps add more flexiblity by visting java project again


def generate_32bit_sha_hash(input_string):
    # Compute the SHA-256 hash
    sha256_hash = hashlib.sha256(input_string.encode()).hexdigest()

    # Take the first 8 characters (32 bits) of the hash and convert them to an integer in decimal form
    truncated_hash = int(sha256_hash[:8], 16)

    return truncated_hash



def create_random_process(and_branches=5,
                          xor_branches=5,
                          loop_weight=0.1,
                          single_activity_weight=0.2,
                          skip_weight=0.1,
                          sequence_weight=0.7,
                          and_weight=0.3,
                          xor_weight=0.3,
                          max_depth=3,
                          data_object_probability=0.1):
    process_id = str(generate_32bit_sha_hash(
        str(datetime.datetime.now().time())))
    storage_path = "processes/process_" + \
        process_id + ".plg"

    command_list = ["java", "-jar", "ProcessGenerator.jar",
                    "-ab", str(and_branches), "-xb", str(xor_branches),
                    "-l", str(loop_weight), "-sa", str(single_activity_weight),
                    "-sw", str(skip_weight), "-sq", str(sequence_weight),
                    "-aw", str(and_weight), "-xw", str(xor_weight),
                    "-md", str(max_depth), "-dop", str(data_object_probability),
                    "-fd", storage_path]

    command = " ".join(map(str, command_list))
    print(command)

    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print("Output:")
    output = result.stdout
    error = result.stderr
    print(output)

    if len(error) == 0:
        print(f"Success: process stored to {storage_path}")
    else:
        print("An error has occured.")
        print("Errors:")
        print(error)

    return storage_path


def create_log_from_model(model_path, mode, no_traces=1000):
    if mode != "testing" and mode != "training":
        print("wrong mode mfer")
        return
    log_id = generate_32bit_sha_hash(str(datetime.datetime.now().time()))

    storage_path = f"../../logs/{mode}/{log_id}.xes"

    command_list = [
        "java", "-jar", "LogGenerator.jar",
        "-l", storage_path,
        "-m", model_path,
        "-c", str(no_traces)
    ]
    command = " ".join(map(str, command_list))
    print(command)
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    print("Output:")
    output = result.stdout
    error = result.stderr
    print(output)

    if len(error) == 0:
        print(f"Success: log stored to {storage_path}")
        return {storage_path}
    else:
        print("An error has occured.")
        print("Errors:")
        print(error)


def create_random_log(index, mode):
    print(f"this is the {index}-th log")

    random_and_branches = random.randint(0, 4)
    random_xor_branches = random.randint(0, 4)
    random_loop_weight = random.uniform(0, 0.5)
    random_single_activity_weight = random.uniform(0, 0.3)
    random_sequence_weight = random.uniform(0.2, 1)
    random_and_weight = random.uniform(0, 0.5)
    random_xor_weight = random.uniform(0, 0.5)
    random_max_depth = random.randint(1, 5)
    random_data_object_probability = random.uniform(0, 0.4)

    cur_proc = create_random_process(and_branches=random_and_branches,
                                     xor_branches=random_xor_branches,
                                     loop_weight=random_loop_weight,
                                     single_activity_weight=random_single_activity_weight,
                                     sequence_weight=random_sequence_weight,
                                     and_weight=random_and_weight,
                                     xor_weight=random_xor_weight,
                                     max_depth=random_max_depth,
                                     data_object_probability=random_data_object_probability)
    return create_log_from_model(cur_proc, mode, random.randint(1000, 1500))


if __name__ == "__main__":
    num_instances = 150
    training_num = math.floor(num_instances *0.7)
    testing_num =   num_instances - training_num


    for i in range(training_num):
        create_random_log(i, "training")
    for i in range(testing_num):
        create_random_log(i, "testing")