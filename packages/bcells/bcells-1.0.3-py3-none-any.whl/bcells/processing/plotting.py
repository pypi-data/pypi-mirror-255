import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def plot_traces(sig, conc, bary=None, ax=None):
    """Plot traces and barycenter for a given concentration.

    Parameters
    ----------
    sig : numpy.ndarray
        Array of traces where the traces are given as rows.
    conc : float
        Concentration of the experiment where the traces were recorded. This 
        is only used for the title.
    bary : numpy.ndarray, optional
        Barycenter of the traces. The default is None. If provided, this is
        supposed to be a 1d-array with the same length as the number of columns
        in sig.

    Returns
    -------
    fig, ax : matplotlib.pyplot.figure, matplotlib.pyplot.axes
        Figure and axes of the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    if bary is not None:
        if sig.shape[1] != len(bary):
            raise ValueError("sig must have the same number of columns as len(bary)")
       
        ax.plot(np.arange(sig.shape[1]) / 2, sig.T, linewidth=0.5, color='gray')
        ax.plot([], [], color='gray', label='standardized traces') # for legend of previous line
        ax.plot(np.arange(sig.shape[1]) / 2, bary, linewidth=0.5, color='blue', label='barycenter')
        ax.legend()
        title = "Traces + Barycenter for {} muM".format(conc)
    else:
        ax.plot(np.arange(sig.shape[1]) / 2, sig.T, linewidth=0.5)
        title = "Traces for {} muM".format(conc)
    ax.set_xlabel("Time (s)")
    ax.set_title(title)
    return ax

def plot_all_charac(dat, y, concs_true, concs_plot, x='conc_plot', ax=None):
    """Plot all characteristics over multiple concentrations in a violin plot.

    Parameters
    ----------
    dat : DataFrame
        DataFrame containing all characteristics for all concentrations.
    y : str
        Name of the column to plot.
    concs_true : list
        List of underlying concentration values.
    concs_plot : list
        List of concentrations to plot.
    x : str, optional
        Name of the column containing the concentrations. The default is 'conc_plot'.
    
    Returns
    -------
    fig, ax : matplotlib.pyplot.figure, matplotlib.pyplot.axes
        Figure and axes of the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    log_x_col = 'log_' + x
    dat[log_x_col] = np.log10(dat[x])
    sns.violinplot(data=dat, inner='quart', x=log_x_col, y=y, native_scale=True)
    tick_labels = [str(int(c)) if ((c >= 1) or (c == 0))  else str(c) for c in concs_true]
    ax.set_xlabel(r"concentration ($\mu M$)")
    ax.set_title(y)
    # set ylimits
    ax.set_ylim(max(0, dat[y].min()), dat[y].max())
    tick_locs = concs_plot
    # plt.xticks(ticks=tick_locs, labels=tick_labels)
    plt.xticks(ticks=np.log10(tick_locs), labels=tick_labels)
    return ax

def plot_charac_barys(dat, y, concs_true, concs_plot, x='conc_plot', ax=None):
    """Scatter plot characteristics of barycenters.

    Parameters
    ----------
    dat : DataFrame
        DataFrame containing all characteristics for all concentrations.
    y : str
        Name of the column to plot.
    concs_true : list
        List of underlying concentration values.
    concs_plot : list
        List of concentrations to plot.
    x : str, optional
        Name of the column containing the concentrations. The default is 'conc_plot'.
    
    Returns
    -------
    fig, ax : matplotlib.pyplot.figure, matplotlib.pyplot.axes
        Figure and axes of the plot.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 5))
    # sns.violinplot(data=dat, inner='quart', x=x, y=y, native_scale=True)
    ax.scatter(concs_plot, dat[y])
    tick_labels = [str(int(c)) if ((c >= 1) or (c == 0))  else str(c) for c in concs_true]
    ax.set_xlabel(r"concentration ($\mu M$)")
    ax.set_title(y)
    ax.set_xscale('log')
    tick_locs = concs_plot
    plt.xticks(ticks=tick_locs, labels=tick_labels)
    # plt.xticks(ticks=np.log10(tick_locs), labels=tick_labels)
    return ax