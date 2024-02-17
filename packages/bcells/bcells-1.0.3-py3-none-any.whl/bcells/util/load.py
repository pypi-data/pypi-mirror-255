import os
import pandas as pd

def files_with_ending(path_to_files_dir, file_ending='.nd2'):
    """Returns a list of files with a certain ending in a directory.

    This functions expects that the files with the desired ending in that 
    directory have the drug concentration in their filename. The drug
    concentration is expected to be in units of µM, muM, or mM and 
    has the following form: 
        '_<concentration><whitespace(optional)><unit>_'.
    
    Parameters
    ----------
    path_to_dir : str
        Path to directory.
    file_ending : str, optional
        File ending. The default is '.nd2'.
    
    Returns
    -------
    filenames : list
        List of filenames sorted according to tetracaine value.
    concs : numpy array
        Array of concentrations in muM sorted in ascending order.
    files : pandas DataFrame
        DataFrame with columns of the split filenames.
    """
    # create pandas dataframe with all files with .nd2 ending in directory
    fnames = [f for f in os.listdir(path_to_files_dir) 
                 if os.path.isfile(os.path.join(path_to_files_dir, f))
                 and f.endswith(file_ending)]
    files = pd.DataFrame(fnames).iloc[:, 0].str.split('_', expand=True)
    n_cols = files.shape[1] 
    original_col_names = files.columns.to_list() # column names for reconstruction later

    # find out the column with the tetracaine concentration
    # throws an error even if all files contain concentration data but not in 
    # the same column as determined by spliting at underscores
    concentration_col = -1
    endings = ['µM', 'mM', 'muM']
    for i in range(n_cols):
        if files.iloc[:, i].str.endswith(tuple(endings)).all():
            concentration_col = i
            break
    if concentration_col == -1:
        raise ValueError("Not all found files contain concentration data in \
                          the same column after splitting at underscores.")

    # get tetracaine concentration in µM
    # conc_col = files.iloc[:, concentration_col]
    conc_name = files.columns[concentration_col]
    # since we expect this to be at the end as endswith returned True and all
    # concentration abbreviations are 2 characters long
    # conc_split = [(s[:-2], s[-2:]) for s in conc_col.to_list()]
    files['conc_fname'] = files[conc_name].apply(lambda x: float(x[:-2].strip()))
    files['unit'] = files[conc_name].apply(lambda x: x[-2:])
    files['concentration'] = files[['conc_fname', 'unit']].apply(lambda x: 1000*x.iloc[0] if x.iloc[1] == "mM" else x.iloc[0], axis=1)
    files.sort_values(by=['concentration'], inplace=True)

    # get filenames in sorted order
    filenames = files[original_col_names].apply(lambda x: '_'.join(x), axis=1).to_list()
    concs = files['concentration'].to_numpy()

    # print information
    print("Found {} files for the following concentrations (in {}):".format(len(filenames), "muM"))
    print("  ".join([str(b) for b in concs]))
    print("The files are:")
    print("\n".join(filenames))
    return filenames, concs, files