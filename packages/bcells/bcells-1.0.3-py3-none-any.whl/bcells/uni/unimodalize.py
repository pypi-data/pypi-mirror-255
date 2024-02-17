# The following code is (partly) taken and adapted from the R package
# "monotone") and more specifically from the unimonotoneC function written in 
# C. The authors of this R package are: Frank Busing, Juan Claramunt Gonzalez


import numpy as np


def unimodalize(x_inp, w_inp=None):
    if len(x_inp.shape) != 1:
        raise ValueError("x must be a one-dimensional array")
    if w_inp is None:
        w = np.ones(shape=len(x_inp), dtype=np.float64)
    else:
        if len(w_inp.shape) != 1:
            raise ValueError("w must be a one-dimensional array")
        # check if both have the same length
        if len(w_inp) != len(x_inp):
            raise ValueError("x and w must have the same length")
        w = np.array(w_inp, dtype=np.float64, copy=True)
    
    # make sure x is of type np.float64 and copy x so that input is not 
    # changed on disk
    x = x_inp.astype(np.float64, copy=True)

    size = len(x)

    # here the code from the "unimonotoneC" function starts
    n = size

    lx = np.zeros(n + 1)
    lw = np.zeros(n + 1)
    ls = np.zeros(n + 1, dtype=int)
    le = np.zeros(n + 1)

    lx[1:] = x
    lw[1:] = w

    ls[1] = 1
    xim1 = lx[1]
    wim1 = lw[1]
    wxx = wim1 * xim1 * xim1
    bxx = wxx
    le[1] = wxx - bxx

    i = 2
    # for i in range(2, n + 1):
    while i <= n:
        xi = lx[i]
        wi = lw[i]
        lastb = i - 1
        csize = 1
        wxx += wi * xi * xi
        if xim1 > xi:
            csize += ls[lastb]
            bxx -= lw[lastb] * lx[lastb] * lx[lastb]
            sumx = wim1 * xim1 + wi * xi
            wi += wim1
            xi = sumx / wi
            le[i] = 1.7976931348623158e+308
            while i < n and xi > lx[i + 1]: # index error if i = n?
                i += 1
                le[i] = 1.7976931348623158e+308
                csize += 1
                sumx += lw[i] * lx[i]
                wi += lw[i]
                xi = sumx / wi
                wxx += lw[i] * lx[i] * lx[i]
            lastb -= ls[lastb]
            while lastb > 0 and lx[lastb] > xi:
                bxx -= lw[lastb] * lx[lastb] * lx[lastb]
                csize += ls[lastb]
                sumx += lw[lastb] * lx[lastb]
                wi += lw[lastb]
                xi = sumx / wi
                lastb -= ls[lastb]
            bxx += sumx * sumx / wi
        else:
            bxx += wi * xi * xi
            le[i] = wxx - bxx
        lx[i] = xim1 = xi
        lw[i] = wim1 = wi
        ls[i] = csize
        i += 1

    # The rest of the code is not provided, so it's not included in this Python function.
    rx = np.zeros(n + 1)
    rw = np.zeros(n + 1)
    rs = np.zeros(n + 1, dtype=int)
    re = np.zeros(n + 1)

    rx[1:] = x
    rw[1:] = w

    rs[n] = 1
    xip1 = rx[n]
    wip1 = rw[n]
    wxx = wip1 * xip1 * xip1
    bxx = wxx
    re[n] = wxx - bxx
    i = n - 1
    # for i in range(n - 1, 0, -1):
    while i > 0:
        xi = rx[i]
        wi = rw[i]
        lastb = i + 1
        csize = 1
        wxx += wi * xi * xi
        if xip1 > xi:
            csize += rs[lastb]
            bxx -= rw[lastb] * rx[lastb] * rx[lastb]
            sumx = wip1 * xip1 + wi * xi
            wi += wip1
            xi = sumx / wi
            re[i] = 1.7976931348623158e+308
            while i > 1 and xi > rx[i - 1]:
                i -= 1
                re[i] = 1.7976931348623158e+308
                csize += 1
                sumx += rw[i] * rx[i]
                wi += rw[i]
                xi = sumx / wi
                wxx += rw[i] * rx[i] * rx[i]
            lastb += rs[lastb]
            while lastb <= n and rx[lastb] > xi:
                bxx -= rw[lastb] * rx[lastb] * rx[lastb]
                csize += rs[lastb]
                sumx += rw[lastb] * rx[lastb]
                wi += rw[lastb]
                xi = sumx / wi
                lastb += rs[lastb]
            bxx += sumx * sumx / wi
        else:
            bxx += wi * xi * xi
            re[i] = wxx - bxx
        rx[i] = xip1 = xi
        rw[i] = wip1 = wi
        rs[i] = csize
        i -= 1

    mode = 0
    work = 0.0
    error = 1.7976931348623158e+308
    for i in range(1, n + 1):
        if ls[i] == 1 and rs[i] == 1 and error > (work := le[i] + re[i]):
            mode = i
            error = work

    if mode != 0: # should always be greater than 0 since start counting at 1?
        # xx = [0] + list(x)
        xx = list(x)
        lk = mode - 1
        while lk > 0:
            xk = lx[lk]
            csize = ls[lk]
            for i in range(1, csize + 1):
                # xx[lk] = xk
                xx[lk - 1] = xk
                lk -= 1
        rk = mode + 1
        while rk < n:
            xk = rx[rk]
            csize = rs[rk]
            for i in range(1, csize + 1):
                # xx[rk] = xk
                xx[rk - 1] = xk
                rk += 1

    return xx