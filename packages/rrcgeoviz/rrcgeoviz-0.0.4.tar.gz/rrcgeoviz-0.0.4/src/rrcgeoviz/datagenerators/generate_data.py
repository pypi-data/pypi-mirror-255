from os import listdir
from os.path import isfile, join
from pathlib import Path
import pickle

from .example import run_example


# add other data generators here
data_generators = {"test_option_name": run_example}


def generate_data(arguments):
    options = arguments.options
    location = None
    should_cache = False

    if "cache_location" in options:
        location = options["cache_location"]
    else:
        location = "/.geovizcache"

    if should_cache:
        Path(location).mkdir(parents=True, exist_ok=True)

    if "cache_results" in options and options["cache_results"]:
        should_cache = True

    if "use_cache" in options and options["use_cache"] == False:
        use_cache = False
    else:
        use_cache = True
    data_dict = {}
    fresh_data_dict = {}

    # generate the data if not found in cache folder
    if use_cache:
        cache_files = [f for f in listdir(location) if isfile(join(location, f))]
    else:
        cache_files = []

    for key, _ in data_generators.items():
        if key in options:
            if str(key) + ".pkl" not in cache_files or use_cache == False:
                result = data_generators[key](arguments)
                data_dict[key] = result
                fresh_data_dict[key] = result
            else:
                read_path = location + "/" + str(key) + ".pkl"
                # print(read_path)
                with open(read_path, "rb") as pickle_file:
                    result = pickle.load(pickle_file)
                data_dict[key] = result

    # if should cache, store the data
    if should_cache:
        print("caching data...")
        for key, value in fresh_data_dict.items():
            filepath = location + "/" + str(key) + ".pkl"
            file = open(filepath, "wb")
            pickle.dump(value, file)
            file.close()

    # print(data_dict)
    return data_dict
