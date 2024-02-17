from os import path
import pickle

def get_example_traces():
    """Fetches the traces from the data directory.

    Returns:
        dict: A dictionary of the traces.
    """
    path_to_folder = '.'
    file_0 = '../src/bcells/data/traces_bg_0muM_subset.pkl'
    file_10 = '../src/bcells/data/traces_bg_10muM_subset.pkl'
    file_1000 = '../src/bcells/data/traces_bg_1000muM_subset.pkl'  
    path_to_file_0 = path.join(path_to_folder, file_0)
    path_to_file_10 = path.join(path_to_folder, file_10)
    path_to_file_1000 = path.join(path_to_folder, file_1000)

    with open(path_to_file_0, "rb") as f:
        dat_0 = pickle.load(f)
    with open(path_to_file_10, "rb") as f:
        dat_10 = pickle.load(f)
    with open(path_to_file_1000, "rb") as f:
        dat_1000 = pickle.load(f)
    return [{'traces': dat_0, 'conc': 0}, {'traces': dat_10, 'conc': 10}, {'traces': dat_1000, 'conc': 1000}]