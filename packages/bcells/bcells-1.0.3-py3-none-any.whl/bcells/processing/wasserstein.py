import numpy as np
import pandas as pd
from ..uni import unimodalize
from bcells.processing.probability_func import positive_to_cdf, cdf_to_quantile
import cvxopt
from scipy.stats import norm

def remove_0(vec, weights=None):
    """Removes 0 entries from a vector and corresponding entries from weights.

    If an entry is zero, the first preceding value which is not zero is 
    additionally assigned the weight of the zero entry.
    
    Parameters
    ----------
    vec : numpy array
        Vector.
    weights : numpy array, optional
        Weights. The default is None.
    
    Returns
    -------
    new_vec : numpy array
        Vector without 0 entries.
    new_weights : numpy array
        Weights without 0 entries.
    """
    new_vec = []
    new_weights = []
    # new_quant = []
    current_length = 0
    zeros_stretch = 0
    zeros_stretch_start = 0

    # if quant is None:
    #     quant = np.arange(len(vec)) / len(vec)
    if weights is None:
        weights = np.ones(len(vec)) / len(vec)
    
    if vec[0] == 0:
        return remove_0(vec[1:], weights[1:] / (1 - weights[0]))
    else:
        for i in range(len(vec)):
            if vec[i] == 0:
                if zeros_stretch == 0:
                    zeros_stretch_start = i

                zeros_stretch += 1
                if i == len(vec) - 1:
                    new_weights[current_length] += sum(weights[zeros_stretch_start:i+1])
            else:
                if zeros_stretch > 0:
                    new_weights[current_length] += sum(weights[zeros_stretch_start:i])
                    zeros_stretch = 0

                new_vec.append(vec[i])
                new_weights.append(weights[i])
                # new_quant.append(quant[i])
                current_length += 1
    return np.array(new_vec), np.array(new_weights) # , np.array(new_quant),

def average_quantiles(cdf, type="mean", percs=None, n=None):
    """Computes the Wasserstein barycenter of the input `sig` where sig is
    assumed to contain pdf's in the rows.

    The barycenter is calculated by first computing the cdf's of the pdf's and
    then calculating quantile values of the cdf's. The quantile values are 
    then averaged over the different cdf's (using the `type` argument to 
    either calculate the mean or the median) to obtain the barycenter.

    Parameters
    ----------
    sig : numpy array
        Discrete probability distributions. This assumes (contrary to previous
        R code) that the traces are in the rows of the array since python and
        numpy operate in row-major order.
    type : str, optional
        Type of barycenter. Options are {'mean', 'median'}. The median 
        corresponds to a more robust version. The default is "mean".
    n : int, optional
        Number of quantiles. The default is 500.
    
    Returns
    -------
    pdf : numpy array
    """
    if percs is None:
        if n is None:
            n = cdf.shape[1]
        percs = np.arange(1, n + 1) / n
    elif len(percs) != cdf.shape[1]:
        raise ValueError("Argument percs has length {}, while argument cdf has {} rows!".format(len(percs), cdf.shape[1]))

    timepoints_scaled_to_0_1 = np.arange(1, cdf.shape[1] + 1) / cdf.shape[1]
    quant_vals = np.row_stack([np.interp(x=percs, xp=cdf[i, :], fp=timepoints_scaled_to_0_1) for i in range(cdf.shape[0])])
    # quant_vals = np.apply_along_axis(cdf_to_quantile, 1, cdf, percs).T

    if type == "mean":
        quant_vals_avg = np.mean(quant_vals, axis=0)
    elif type == "median":
        quant_vals_avg = np.median(quant_vals, axis=0)
    else:
        raise ValueError("Argument type is not valid!")

    cdf_avg = np.interp(x=percs, xp=quant_vals_avg, fp=percs)

    # first version
    # pdf_avg = np.diff(np.concatenate([[0], quant_vals_avg])) # recover q_s_avg by np.cumsum(pdf)

    # second version
    # quant_vals_avg_diff = np.diff(np.concatenate([[0], quant_vals_avg]))
    # if np.any(quant_vals_avg_diff == 0):
    #     raise ValueError("pdf contains 0! Cannot divide by 0!")
    # n = len(quant_vals_avg_diff)
    # quant_diff_uni = unimonotone.unimodalize((np.ones(n) / n) / quant_vals_avg_diff, w=quant_vals_avg_diff)

    return quant_vals_avg, cdf_avg

# create sparse unimodal constraint matrix
def create_uni_const_sparse(n, k):
    entries = np.concatenate([np.concatenate([-np.ones(max(k-1, 0)), np.ones(n-max(k-1, 0)-2)]), 
                              np.concatenate([2*np.ones(k), -2*np.ones(n-k-1)]),
                              np.concatenate([-np.ones(k), np.ones(n-k-1)])])
    row_coords = np.concatenate([np.arange(1, n-1), np.arange(n-1), np.arange(n-1)])
    col_coords = np.concatenate([np.arange(n-2), np.arange(n-1), np.arange(1, n)])
    return cvxopt.spmatrix(entries, I=row_coords, J=col_coords, size=(n-1, n))

def create_cdf_const_sparse_m(n, mode):
    # 0 <= mode <= n-1
    entries = np.concatenate([np.ones(n - mode), -np.ones(n-1-mode)])
    row_coords = np.concatenate([np.arange(0, n-mode), np.arange(n-1-mode)])
    col_coords = np.concatenate([np.arange(mode, n), np.arange(mode + 1, n)])
    return cvxopt.spmatrix(entries, I=row_coords, J=col_coords, size=(n-mode, n))

def create_easy_cdf_const_sparse_m(n):
    """
    Creates a matrix C such that CG <= 0 is equivalent to
    G being a cdf (i.e. G_1 <= G_2 <= ... <= G_n and 0 <= G_1 and G_n <= 1)
    """
    entries = np.concatenate([np.array([-1.0]), np.ones(n-1), -np.ones(n-1), np.array([1.0])])
    row_coords = np.concatenate([np.array([0]), np.arange(1, n), np.arange(1, n), np.array([n])])
    col_coords = np.concatenate([np.array([0]), np.arange(n-1), np.arange(1, n), np.array([n-1])])
    return cvxopt.spmatrix(entries, I=row_coords, J=col_coords, size=(n+1, n))

def create_obj(n, m):
    return cvxopt.matrix(np.concatenate([np.ones(n * m), np.zeros(n)]), size=(n * (m + 1), 1))

def create_constraintmat(n, m, mode):
    minus_i_sparse = cvxopt.spmatrix(-1.0, I=np.arange(n * m), J=np.arange(n * m)) # sparse cvxopt matrix
    minus_i_sparse_and_zero = cvxopt.spmatrix(-1.0, I=np.arange(n * m), J=np.arange(n * m), size=(n*(m+1)+n, n*m)) # sparse cvxopt matrix
    s_sparse = cvxopt.spmatrix(1.0, I=np.arange(n * m), J=np.tile(np.arange(n), m), size=(n*m, n)) # sparse cvxopt matrix
    uni_sparse = create_uni_const_sparse(n, mode) # make G cdf with unimodal pdf
    cdf_sparse = create_easy_cdf_const_sparse_m(n) # make G a cdf
    # non_neg = cvxopt.spmatrix(-1.0, I=np.arange(n*(m+1)), J=np.arange(n*(m+1)), size=(n*(m+1), n*(m+1))) # all variables non-negative

    A = cvxopt.sparse([[minus_i_sparse, minus_i_sparse_and_zero], [s_sparse, -s_sparse, uni_sparse, cdf_sparse]])
    return A

def create_constraintvec(cdfs):
    n = cdfs.shape[1]
    cdfs_1d = cdfs.flatten()
    return cvxopt.matrix(np.concatenate([cdfs_1d, -cdfs_1d, np.zeros(n-1), np.zeros(n), np.array([1.0])]))

def create_primalstart(mode, cdfs, A, b, start_cdf=None):
    """Creates a starting distribution for lp solver.
    """
    if start_cdf is None:
        n = cdfs.shape[1]
        start_cdf = norm.cdf(np.arange(n), loc=mode, scale=n/15)

    alpha_norm_cdf = np.abs(cdfs - start_cdf.reshape((1, -1))).flatten()
    primalstart = {'x': cvxopt.matrix(np.concatenate([alpha_norm_cdf, start_cdf]))}
    # add value to make slack variable s positive
    primalstart['s'] = b - A * primalstart['x']
    minimum = np.array(primalstart['s']).min()
    if minimum <= 0:
        primalstart['s'] += -minimum + 1e-7
    return primalstart

def shift(vec, l):
    n = len(vec)
    new_vec = np.zeros(n)
    if l >= 0:
        new_vec[:l] = vec[0]
        new_vec[l:] = vec[:-l]
    elif l < 0:
        l = -l
        new_vec[:-l] = vec[l:]
        new_vec[-l:] = vec[-1]
    return new_vec

def extract_pdf_from_sol(sol, n, m):
    G = np.array(sol['x'][n*m:]).reshape((-1)) # [n*m:n*(m+1)]
    return np.gradient(G)

def l1_bary_unimodal(sig, start_mode=0, end_mode=None):
    """
    
    We calculate (using the linear programming solver cvxopt) the linear
    programming problem of finding the L^1 barycenter under the shape 
    constraint of a unimodal pdf. The solver solves the problem
    minimize c^T x
    subject to Gx + s = h 
    (which should be equivalent to Gx <= h since s is a nonnegative slack
    variable)

    Let m be the number of traces and n be the number time points.
    To do this, we initialize c to be of size m*n + n = n*(m+1) so that
    the first n variables correspond to the distances of the barycenter to the
    given traces. The last n variables correspond to the barycenter.
    """
    if len(sig.shape) != 2:
        raise ValueError("Argument sig not two dimensional, but has dimensions {}.".format(str(sig.shape)))

    m, n = sig.shape

    mode = start_mode
    if end_mode is None:
        end_mode = n-1

    cdfs = positive_to_cdf(sig)

    c = create_obj(n, m)
    A = create_constraintmat(n, m, mode)
    b = create_constraintvec(cdfs)

    use_prev_sol = True
    primal_costs = np.zeros(end_mode - start_mode + 1)
    dual_costs = np.zeros(end_mode - start_mode + 1)
    min_cost = np.inf
    min_mode = None
    while mode <= end_mode:
        if (mode > start_mode) and use_prev_sol:
            primalstart_shifted = create_primalstart(mode=mode, cdfs=cdfs, A=A, b=b, start_cdf=prev_sol_cdf)
            sol = cvxopt.solvers.lp(c=c, G=A, h=b, primalstart=primalstart_shifted)
        else:
            primalstart_gaussian = create_primalstart(mode=mode, cdfs=cdfs, A=A, b=b)
            sol = cvxopt.solvers.lp(c=c, G=A, h=b, primalstart=primalstart_gaussian)

        primal_costs[mode - start_mode] = sol["primal objective"]
        dual_costs[mode - start_mode] = sol["dual objective"]
        if sol["primal objective"] < min_cost:
            min_cost = sol["primal objective"]
            min_mode = mode
            best_sol = sol # alternative to next line and list with all solutions since this might be memory intensive
        prev_sol_cdf = np.cumsum(shift(extract_pdf_from_sol(sol, n, m), 1))
        
        # A[2*n*m + mode, :] *= -1 # change unimodal constraint one mode further
        mode += 1

    stats = {'primal objective': primal_costs, 'dual objective': dual_costs}
    return best_sol, min_cost, min_mode, stats

def l1_bary_unimodal_np(pdfs, modes=None, method="Rsymphony", time_limit=None):
    if len(pdfs.shape) != 2:
        print("Error: Argument pdfs is not two dimensional")
        return -1
    if modes is None:
        modes = np.arange(n)

    n, m = pdfs.shape
    cdfs = positive_to_cdf(pdfs)


    # create objective vector
    obj = np.concatenate((np.ones(n * m), np.zeros(n)))

    # create constraint matrix (only part independant of loop)
    i = np.diag(np.ones(n * m))
    # i = sp_diags(np.ones(n * m))
    s = np.vstack([np.diag(np.ones(n)) for _ in range(m)])
    # s = sp_vstack([sp_diags(np.ones(n)) for _ in range(m)])
    z1 = np.zeros((n - 1, n * m))
    # z1 = csc_matrix((n - 1, n * m))
    
    diags_u = [np.ones(n - 2), -2 * np.ones(n - 1), np.ones(n - 1)]
    offsets = [-1, 0, 1]
    u = sum([np.diag(diags_u[i], k=offsets[i]) for i in range(len(diags_u))])
    # u = sp_diags(diags_u, offsets=[-1, 0, 1])

    mat_independent_of_mode = np.vstack((np.hstack((i, -s)), np.hstack((i, s)), np.hstack((z1, u))))
    # mat_independent_of_mode = sp_vstack((sp_hstack((i, -s)), sp_hstack((i, s)), sp_hstack((z1, u))))

    # create parts for matrix which in the same rectangle as parts depending on mode
    z2_n = np.zeros((n, n * m))
    # z2_n = csc_matrix((n, n * m))
    diags_c_n = [np.ones(n), -np.ones(n - 1)]
    offsets = [0, 1]
    c_n = sum([np.diag(diags_c_n[i], k=offsets[i]) for i in range(len(diags_c_n))])
    # c_n = sp_diags(diags_c_n, offsets=[0, 1])
    z2_c_n = np.hstack((z2_n, c_n))
    # z2_c_n = sp_hstack((z2_n, c_n))

    # create vector which indicates the direction of the inequalities
    dir_independent_of_mode = np.concatenate((np.ones(n * m), np.ones(n * m)))

    # create right hand side of inequalities
    cdfs_vector = cdfs.flatten()
    rhs_independent_of_mode = np.concatenate((-cdfs_vector, cdfs_vector, np.zeros(n - 1)))

    solutions = []
    p = len(modes)
    for k in range(p):
        print(f"{k+1}/{p}")
        mode = modes[k]

        mat = np.vstack((mat_independent_of_mode, z2_c_n[mode:n, ]))
        # mat = sp_vstack((mat_independent_of_mode, z2_c_n[mode:n, ]))

        dir = np.concatenate((dir_independent_of_mode, np.ones(mode - 1), -np.ones(n - mode), [0]))

        rhs = np.concatenate((rhs_independent_of_mode, np.zeros(n - mode), [1]))

        # Solve the linear programming problem
        # This is a placeholder, replace with your preferred method
        # sol_k = cp.Variable()

        # solutions.append(sol_k)

    min_index = np.argmin([sol.value for sol in solutions])
    min_mode = modes[min_index]

    sol = solutions[min_index]

    return sol

# write function that calculates the generalized inverse of a cdf (i.e. the inverse of the cdf)
# where the cdf is given as a vector of probabilities
def generalized_inverse(vec_cdf, p_s=None):
    n_points = len(vec_cdf)
    if p_s is None:
        p_s = np.arange(1, n_points + 1) / n_points
    return np.interp(p_s, vec_cdf, np.arange(n_points)) / (n_points - 1)

def approx_bary(sig, method="mean", n=None, fps=2):
    """Computes the Wasserstein barycenter of a set of discrete probability
    distributions.

    Parameters
    ----------
    sig : numpy array
        Discrete probability distributions. This assumes (contrary to previous
        R code) that the traces are in the rows of the array since python and
        numpy operate in row-major order.
    method : str, optional
        Type of barycenter. Options are {'mean', 'median'}. The median 
        corresponds to a more robust version. The default is "mean".
    n : int, optional
        Number of quantiles. The default is the number of frames/time points.
    
    Returns
    -------
    x : numpy array
        Quantiles.
    unimodal_curve : numpy array
        Unimodal curve.
    """
    # assumes that traces are in rows for possible speedup (since numpy operates in row-major)

    # assuming that sig is non-negative, these transformations create cdf's
    cdfs = positive_to_cdf(sig)

    # apply cdf_to_quantile function to each column
    # p_s = np.arange(n) / (n - 1) # Is the last entry determined anyway?
    # qv = np.apply_along_axis(cdf_to_quantile, 1, cdfs, p_s)
    if n is None:
        cdfs_inv = np.apply_along_axis(generalized_inverse, 1, cdfs)
    else:
        p_s = np.arange(1, n + 1) / n
        cdfs_inv = np.apply_along_axis(generalized_inverse, 1, cdfs, p_s)
    if method == "mean":
        cdfs_inv_avg = np.mean(cdfs_inv, axis=0)
    elif method == "median":
        cdfs_inv_avg = np.median(cdfs_inv, axis=0)
    else:
        raise ValueError("Argument type is not valid!")
    
    cdf_inv_avg_inv = generalized_inverse(cdfs_inv_avg)
    pdf = np.gradient(cdf_inv_avg_inv)

    # cdfs_inv_avg_grad = np.gradient(cdfs_inv_avg)
    # weights = np.repeat(1 / len(cdfs_inv_avg_grad), len(cdfs_inv_avg_grad))
    # unimodal_curve = unimonotone.unimodalize(weights / cdfs_inv_avg_grad)
    # unimodal_curve = unimonotone.unimodalize(weights / cdfs_inv_avg_grad, w=cdfs_inv_avg_grad)
    x = np.arange(len(pdf)) * (cdfs.shape[1] / (fps * len(pdf))) # n = len(pdf) should be true
    return x, pdf #, unimodal_curve

def approx_bary_2(sig, method="mean", n=None, fps=2):
    """Computes the Wasserstein barycenter of a set of discrete probability
    distributions.

    Parameters
    ----------
    sig : numpy array
        Discrete probability distributions. This assumes (contrary to previous
        R code) that the traces are in the rows of the array since python and
        numpy operate in row-major order.
    method : str, optional
        Type of barycenter. Options are {'mean', 'median'}. The median 
        corresponds to a more robust version. The default is "mean".
    n : int, optional
        Number of quantiles. The default is 500.
    
    Returns
    -------
    x : numpy array
        Quantiles.
    unimodal_curve : numpy array
        Unimodal curve.
    """
    cdfs = positive_to_cdf(sig)
    if n is None:
        n = cdfs.shape[1]
    p_s = np.arange(1, n + 1) / n
    cdfs_inv = np.apply_along_axis(generalized_inverse, 1, cdfs, p_s)

    if method == "mean":
        cdfs_inv_avg = np.mean(cdfs_inv, axis=0)
    elif method == "median":
        cdfs_inv_avg = np.median(cdfs_inv, axis=0)
    else:
        raise ValueError("Argument type is not valid!")
    
    cdfs_inv_avg_grad = np.gradient(cdfs_inv_avg)
    weights = np.repeat(1 / len(cdfs_inv_avg_grad), len(cdfs_inv_avg_grad))
    unimodal_curve = unimodalize.unimodalize(weights / cdfs_inv_avg_grad)
    
    x = np.arange(len(unimodal_curve)) * (cdfs.shape[1] / (fps * len(unimodal_curve))) # n = len(pdf) should be true
    return x, unimodal_curve, cdfs_inv_avg
