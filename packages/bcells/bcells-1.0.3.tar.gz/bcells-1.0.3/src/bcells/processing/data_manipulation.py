import pandas as pd
import numpy as np
from . import characteristic_func  # replace with the name of your file (without .py)

def create_charac_trace(trace, characteristics, x=None):
    """
    Calculate characteristics for a vector containing a trace

    Parameters
    ----------
    trace (np.ndarray): a 1D array corresponding to a trace
    characteristics (list): list of names of characteristic functions to compute
    x (np.ndarray, optional): optional 1D array of x values if the trace is evaluated at non-equidistant points

    Returns
    ----------
    dict: the calculated characteristics in a dictionary with the characteristics as keys
    
    Note
    ----
    This function requires the import of the module `characteristic_func`.
    """
    if x is None:
        res = [(getattr(characteristic_func, fun_name, None))(trace) for fun_name in characteristics]
    else:
        res = [(getattr(characteristic_func, fun_name, None))(trace, x) for fun_name in characteristics]
    return np.array(res)
    # return pd.Series(res, index=characteristics)

def create_charac_df(trace_mat, characteristics, x_mat=None, ind=None):
    """
    Calculate characteristics for a matrix containing traces

    Parameters
    ----------
    trace_mat (np.ndarray): a 2D array where each row is a trace
    characteristics (list): list of names of characteristic functions to compute
    x_mat (np.ndarray, optional): optional 2D array of x values if the traces are evaluated at non-equidistant points
    ind (np.ndarray, optional): optional 1D array of indices for the rows of trace_mat i.e. the traces/cells

    Returns
    ----------
    pd.DataFrame: the calculated characteristics in a DataFrame with the
        characteristics as columns and the traces as rows

    Note
    ----
    This function requires the import of the module `characteristic_func`.
    """

    if x_mat is None:
        # need to test whether the right shape is returned
        # res = [np.apply_along_axis(getattr(characteristic_func, fun_name, None), 1, trace_mat) for fun_name in characteristics]
        # res = np.array(res).T

        # probably slower than previous lines
        res = np.apply_along_axis(create_charac_trace, 1, trace_mat, characteristics) # iterates over traces -> probably slower than previuos line
    else:
        if trace_mat.shape != x_mat.shape:
            raise ValueError(f"Inputs trace_mat and x_mat do not have the same shape!\n  trace_mat has shape {trace_mat.shape}, while x_mat has shape {x_mat.shape}.")
        res = np.empty((trace_mat.shape[0], len(characteristics)))
        for i in range(trace_mat.shape[0]):
            res[i,] = create_charac_trace(trace_mat[i, :], characteristics, x_mat[i, :])

    if ind is None:
        ind = np.arange(1, trace_mat.shape[0] + 1, dtype=np.int64)
    return pd.DataFrame(res, columns=characteristics, index=ind)