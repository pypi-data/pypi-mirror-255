import numpy as np

def positive_to_cdf(positive):
    """Assumes that the array is nonnegative everywhere and thus can
    be interpreted as an (unnormalized) pdf.

    If the array is 2d, the pdf's (or positive functions) are assumed to be
    in the rows. That means, that we calculate the cumulative sums of 
    each row. If the array is transposed, this method will give the wrong
    result.

    Parameters:
    positive (numpy.ndarray): a 1D or 2D array with non-negative entries

    Returns:
    numpy.ndarray: a 1D or 2D array which represents the cumulative distribution function
    """
    if len(positive.shape) == 1:  # if positive is a 1D array
        cdfs = np.cumsum(positive)
        cdfs /= cdfs[-1]
    else:  # if positive is a 2D array
        cdfs = np.cumsum(positive, axis=1)
        cdfs /= cdfs[:, -1][:, np.newaxis]
    return cdfs

def cdf_to_quantile(cdf, ps):
    """Converts percentiles ps to quantiles given a discrete cdf.
    
    Parameters
    ----------
    cdf : numpy array
        Discrete cumulative distribution function.
    ps : numpy array
        Percentiles.
    
    Returns
    -------
    qv : numpy array
        Quantiles.
    """
    tol = 1e-8
    qv = np.zeros(len(ps))
    for i in range(len(ps)):
        qv[i] = np.min(np.where(cdf >= ps[i] - tol)) / len(cdf)
    return qv

def quantiles(cdf, N=None):
    n = len(cdf)
    range_points = np.arange(n) / (n - 1)
    if N is None:
        p_s = np.arange(n) / (n - 1)
    else:
        p_s = np.arange(N) / (N - 1)
    q_s = np.quantile(a=cdf, q=p_s, alpha=0, beta=1, axis=1)
    return np.interp(range_points, cdf, np.arange(n)) / (n - 1)