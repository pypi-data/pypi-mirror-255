import numpy as np

def divide_by_abs_mean_before_light(trace, x=None, light_on=60, fps=2):
    """
    Divide by the average value during the first 60 seconds (which correspond to 120 frames)

    Parameters
    ----------
    trace (np.ndarray): a 1D array
    x (np.ndarray, optional): a 1D array of the same length as `trace`
    light_on (int, optional): the time in seconds when the light turns on, default is 60 seconds
    fps (int, optional): frames per second, default is 2 frames per second
    
    Returns
    ----------
    np.ndarray: the `trace` divided by the absolute mean of the first 60 seconds
    """
    if x is not None:
        return trace / abs(np.mean(trace[x <= light_on]))
    return trace / abs(np.mean(trace[:(light_on * fps)]))

def stand60(sig, x=None, light_on=60, fps=2):
    """
    Standardize each row of `sig` by dividing by the absolute mean of the first `light_on` seconds

    This function assumes that mean of the first `light_on` seconds is positive.

    Parameters
    ----------
    sig (np.ndarray): a 2D array where each row is a signal to be standardized
    x (np.ndarray, optional): a 2D array of the same shape as `sig` where each row represents time points corresponding to the signal
    light_on (int, optional): the time in seconds when the light turns on, default is 60 seconds
    fps (int, optional): frames per second, default is 2 frames per second

    Returns
    ----------
    np.ndarray: the `sig` array with each row divided by the absolute mean of the first `light_on` seconds
    """
    # vectorized version 
    if x is not None:
        return sig / np.mean(sig[x <= light_on], axis=1)[:, np.newaxis]
    else:
        return sig / np.mean(sig[:, :(light_on * fps)], axis=1)[:, np.newaxis]

    # non-vecctorized version
    # if x is not None:
    #     return np.array([divide_by_abs_mean_before_light(row, x_row, light_on, fps) for row, x_row in zip(sig, x)])
    # return np.array([divide_by_abs_mean_before_light(row, None, light_on, fps) for row in sig])

def keep_greater_than_0_traces(sig):
    """
    Keep only the traces where all elements are greater than 0

    Parameters
    ----------
    sig (np.ndarray): a 2D array where each row is a trace

    Returns
    ----------
    np.ndarray: a 2D array containing only the traces where all elements are greater than 0
    """
    return sig[np.all(sig > 0, axis=1), :]