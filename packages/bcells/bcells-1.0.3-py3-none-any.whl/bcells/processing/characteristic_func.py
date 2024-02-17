import numpy as np
from .probability_func import positive_to_cdf

def shortest_int(trace, mass_thresh=0.25, x=None):
    """
    Calculate the smallest (shortest) interval which contains at least `massPerc` of the total mass of the trace.

    The `trace` is assumed to be non-negative everywhere and then normalized to have mass 1, i.e. be a density.
    `mass_thresh` signifies which portion of the total mass (which is 1) should at least be contained in the 
    interval. `x` is an optional vector which further specifies the time points of the recorded values in `trace`.
    This is necessary if the time points are not equally spaced. The function returns the given interval in seconds
    where, if no `x` is given, it is assumed that the time points are equally spaced with distance 1/2, i.e. 
    x = 1:length(trace) / 2 gives the same result as if no x is specified. This is done because the values in 
    `trace` are assumed to be recorded every 0.5 seconds. In that case, the returned interval is the result in 
    seconds.

    Parameters
    ----------
    trace (numpy.ndarray): a vector with non-negative entries
    mass_thresh (float): a number between 0 and 1 which specifies the mass threshold
    x (numpy.ndarray, optional): a vector of the same length as `trace` which specifies the time points of the trace

    Returns
    ----------
    list: a vector of length 2 which contains the start and end point of the interval

    Examples
    ----------
    trace = np.arange(1, 11) + np.arange(10, 0, -1)
    shortest_int(trace, mass_thresh = 0.25, x = np.arange(len(trace)))
    """
    N = len(trace)
    cdf = positive_to_cdf(trace)
    shortestIntStartIndex = 0
    shortestIntEndIndex = np.argmax(cdf >= mass_thresh)

    if x is None:
        shortestIntLength = shortestIntEndIndex - shortestIntStartIndex
        for i in range(1, N - shortestIntLength):
            j = min(i + shortestIntLength, N - 1)
            while j >= i:
                if cdf[j] - cdf[i - 1] < mass_thresh:
                    break
                shortestIntStartIndex = i
                shortestIntEndIndex = j
                shortestIntLength = j - i
                j -= 1

        max_mass = 0
        for i in range(N - shortestIntLength):
            mass = cdf[i + shortestIntLength] - cdf[i - 1] if i >= 1 else cdf[i + shortestIntLength]
            if mass > max_mass:
                shortestIntStartIndex = i
                shortestIntEndIndex = i + shortestIntLength
                max_mass = mass

            # find all starting points with equal or very close mass and choose middle
        tol = 1e-6
        shortestIntStartIndices = []
        for i in range(N - shortestIntLength):
            if i >= 1:
                mass = cdf[i + shortestIntLength] - cdf[i - 1]
            else:
                mass = cdf[i + shortestIntLength]
            if mass > max_mass - tol:
                shortestIntStartIndices.append(i)
        shortestIntStartIndex = round((min(shortestIntStartIndices) + max(shortestIntStartIndices)) / 2)
        shortestIntEndIndex = shortestIntStartIndex + shortestIntLength
        # divide by half to get the time in seconds of the interval and not the indices
        interval = [shortestIntStartIndex / 2, shortestIntEndIndex / 2]
    else:
        x_shortestIntLength = x[shortestIntEndIndex] - x[shortestIntStartIndex]
        for i in range(1, N):
            x_end = min(x[i] + x_shortestIntLength, x[N-1])
            # j is the first index (which is smaller than x[N - 1]), such that with 
            # starting index i the time interval between i and j is smaller than the
            # current shortest x_shortestIntLength)

            # j = min(max([k for k, val in enumerate(x) if val >= x_end]) - 1, x[N-1])
            j = min(np.argmax(x >= x_end) - 1, x[N - 1]) # minus 1 to be smaller actually smaller than the previous shortest interval
            
            while j >= i: 
                if cdf[j] - cdf[i - 1] < mass_thresh:
                    break
                shortestIntStartIndex = i
                shortestIntEndIndex = j
                x_shortestIntLength = x[j] - x[i]
                j = j - 1
        # check if there exists an interval of same length with larger mass later
        max_mass = cdf[shortestIntEndIndex]
        if shortestIntStartIndex >= 1:
            max_mass = max_mass - cdf[shortestIntStartIndex - 1]

        for i in range(shortestIntStartIndex + 1, N):
            # j = max([k for k, val in enumerate(x) if val >= x[i] + x_shortestIntLength])
            j = np.argmax(x >= (x[i] + x_shortestIntLength))
            if j > N:
                break

            tol = 1e-7
            if x[j] - x[i] <= x_shortestIntLength + tol:
                mass = cdf[j] - cdf[i - 1]
                if mass > max_mass:
                    shortestIntStartIndex = i
                    shortestIntEndIndex = j
                    x_shortestIntLength = x[shortestIntEndIndex] - x[shortestIntStartIndex]
                    max_mass = cdf[j] - cdf[i - 1]
        
        interval = [x[shortestIntStartIndex], x[shortestIntEndIndex]]
    return interval

def length_shortest_int(trace, mass_thresh=0.25, x=None):
    """
    Calculate the length of the shortest interval which contains at least `mass_thresh` of the total mass of the trace.

    The `trace` is assumed to be non-negative everywhere and then normalized to have mass 1, i.e. be a density.
    `mass_thresh` signifies which portion of the total mass (which is 1) should at least be contained in the 
    interval. `x` is an optional array which further specifies the time points of the recorded values in `trace`.
    This is necessary if the time points are not equally spaced. The function returns the length of the interval
    in seconds where, if no `x` is given, it is assumed that the time points are equally spaced with distance 1/2, 
    i.e. x = np.arange(1, len(trace) + 1) / 2 gives the same result as if no x is specified. This is done because 
    the values in `trace` are assumed to be recorded every 0.5 seconds. In that case, the returned length of the 
    interval is in units of seconds.

    Parameters:
    trace (np.ndarray): A numpy array with non-negative entries.
    mass_thresh (float): A number between 0 and 1 which specifies the mass threshold.
    x (np.ndarray, optional): A numpy array of the same length as `trace` which specifies the time points of the trace.

    Returns:
    float: A number which is the length of the shortest interval containing at least `mass_thresh` of the total mass
    of the trace.
    """
    interval = shortest_int(trace, mass_thresh=mass_thresh, x=x)
    return interval[1] - interval[0]

def length_shortest_int_40(trace, x=None):
    """
    This function is a wrapper around the `length_shortest_int` function with a fixed `mass_thresh` of 0.40.

    Parameters:
    trace (np.ndarray): A numpy array with non-negative entries.
    x (np.ndarray, optional): A numpy array of the same length as `trace` which specifies the time points of the trace.

    Returns:
    float: A number which is the length of the shortest interval containing at least 0.40 of the total mass
    of the trace.
    """
    return length_shortest_int(trace, mass_thresh=0.40, x=x)

def midpoint_mass(trace, mass_thresh=0.25, x=None):
    """
    Calculate the midpoint of the shortest interval which contains at least `mass_thresh` of the total mass of the trace.

    Parameters:
    trace: A sequence with non-negative entries.
    mass_thresh (float): A number between 0 and 1 which specifies the mass threshold.
    x: A sequence of the same length as `trace` which specifies the time points of the trace.

    Returns:
    float: A number which is the midpoint of the shortest interval containing at least `mass_thresh` of the total mass
    of the trace.
    """
    interval = shortest_int(trace, mass_thresh=mass_thresh, x=x)
    return sum(interval) / 2

def midpoint_mass_12(trace, x=None):
    """
    This function is a wrapper around the `midpoint_mass` function with a fixed `mass_thresh` of 0.12.

    Parameters:
    trace: A sequence with non-negative entries.
    x: A sequence of the same length as `trace` which specifies the time points of the trace.

    Returns:
    float: A number which is the midpoint of the shortest interval containing at least 0.12 of the total mass
    of the trace.
    """
    return midpoint_mass(trace, mass_thresh=0.12, x=x)

def midpoint_mass_5(trace, x=None):
    """
    This function is a wrapper around the `midpoint_mass` function with a fixed `mass_thresh` of 0.05.

    Parameters:
    trace: A sequence with non-negative entries.
    x: A sequence of the same length as `trace` which specifies the time points of the trace.

    Returns:
    float: A number which is the midpoint of the shortest interval containing at least 0.05 of the total mass
    of the trace.
    """
    return midpoint_mass(trace, mass_thresh=0.05, x=x)

def midpoint_mass_40(trace, x=None):
    """
    This function is a wrapper around the `midpoint_mass` function with a fixed `mass_thresh` of 0.40.

    Parameters:
    trace: A sequence with non-negative entries.
    x: A sequence of the same length as `trace` which specifies the time points of the trace.

    Returns:
    float: A number which is the midpoint of the shortest interval containing at least 0.40 of the total mass
    of the trace.
    """
    return midpoint_mass(trace, mass_thresh=0.4, x=x)

def peak_time(trace, x=None, tol=1e-5):
    """Calculate the time point of the maximum value in the trace.

    If no `x` is given, it is assumed that the time points are equally spaced 
    with distance 1/2, i.e. basically assuming that the frames per second of 
    the recording is 2.

    Parameters
    ----------
    trace: A sequence with non-negative entries.
    x: A sequence of the same length as `trace` which specifies the time points of the trace.
    tol: A small number to determine if multiple values are close to the maximum.

    Returns
    ----------
    float: The time point of the maximum value in the trace.
    """
    max_loc = trace.argmax()
    
    # Check if there are approximately multiple values attaining the maximum. If yes,
    # the mean of the first and last index attaining the maximum.
    close_to_max = trace >= (trace.max() - tol)
    if close_to_max.sum() >= 2:
        first_index_max = close_to_max.argmax()
        last_index_max = len(close_to_max) - close_to_max[::-1].argmax()
        max_loc = round((first_index_max + last_index_max) / 2)
    
    if x is None:
        return max_loc / 2
    else:
        return x[max_loc]

def peak_value(trace):
    """
    Calculate the maximum value in the trace.

    Parameters:
    trace: A sequence with non-negative entries.

    Returns:
    float: The maximum value in the trace.
    """
    return trace.max()
