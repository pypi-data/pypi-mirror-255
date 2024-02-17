import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gc

def create_output_dirs(path, identifier=None):
    """Create output directory in `path`.

    Raises an error if the directory already exists.

    Parameters
    ----------
    path : str
        Path to the directory where the output directory should be created.
    identifier : str, optional
        Identifier for the output directory to make it unique. If not given, 
        the current date and time is used.
    
    Returns
    ----------
    dict
        Dictionary with the paths to the subdirectories of the output directory
        where some files are supposed to be created.
    """

    ### create names of directories
    output_dir_name = '_'.join(['output', 'bcells']) # , dateandtime])
    # subfolders of output_dir
    calc_dir_name = 'calculation_results'
    image_dir_name = 'images'
    # subfolders of image_dir
    seg_dir_name = 'segmentation'
    bary_dir_name = 'barycenters'
    charac_dir_name = 'characteristics'

    ### create directories
    os.makedirs(os.path.join(path, output_dir_name), exist_ok=False)
    os.makedirs(os.path.join(path, output_dir_name, calc_dir_name), exist_ok=False)
    os.makedirs(os.path.join(path, output_dir_name, image_dir_name), exist_ok=False)
    os.makedirs(os.path.join(path, output_dir_name, image_dir_name, seg_dir_name), exist_ok=False)
    os.makedirs(os.path.join(path, output_dir_name, image_dir_name, bary_dir_name), exist_ok=False)
    os.makedirs(os.path.join(path, output_dir_name, image_dir_name, charac_dir_name), exist_ok=False)

    return {'calc_dir': os.path.join(path, output_dir_name, calc_dir_name),
            'seg_dir': os.path.join(path, output_dir_name, image_dir_name, seg_dir_name),
            'bary_dir': os.path.join(path, output_dir_name, image_dir_name, bary_dir_name),
            'charac_dir': os.path.join(path, output_dir_name, image_dir_name, charac_dir_name)}

# pretty useless
def store_arr_or_df(obj, filename, path):
    """Store numpy and pandas lists in a given path.

    The input object `obj` can be either a numpy array or a pandas DataFrame.
    If it is a numpy array, it is stored as a .npy file and if it is a pandas
    DataFrame, it is stored as a .pkl file. If it is neither of these two, a 
    TypeError is raised. 

    Parameters
    ----------
    obj : ndarray or pd.DataFrame
        Object to store.
    filename : str
        Name of the file.
    path : str
        Path to the directory where the file should be stored.
    """
    
    if isinstance(obj, np.ndarray):
        np.save(os.path.join(path, filename + '.npy'), obj)
    elif isinstance(obj, pd.DataFrame):
        obj.to_pickle(os.path.join(path, filename + '.pkl'))
    else:
        raise TypeError('Object type not supported. Is neither np.ndarray' +
                        ' nor pd.DataFrame.')

# store plots
def store_plot(fig, filename, path):
    """Store a matplotlib figure in a given path.

    The figure is stored as a .png file and the plot is cleared afterwards.
    Furthermore, the figure is closed and the memory is freed. 

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to store.
    filename : str
        Name of the file.
    path : str
        Path to the directory where the file should be stored.
    """

    fig.savefig(os.path.join(path, filename + '.png'))
    fig.clf()
    plt.close(fig)
    gc.collect()
