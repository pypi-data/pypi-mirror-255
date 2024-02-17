import numpy as np
import pandas as pd
from skimage import measure

def seg_properties(seg_lbl, imgs):
    """Calculates the properties of the segmented cells.

    This function assumes that the last(!) dimension of imgs is the time 
    dimension.

    Parameters
    ----------
    seg_lbl : (M, N) ndarray
        Segmented and labeled image.
    imgs : (M, N, P) ndarray
        Image sequence where the last(!) dimension is assumed to be the time
        dimension.
    
    Returns
    -------
    cells : pandas DataFrame
        Contains the properties of the segemented cells.
    """
    properties = ['label', 'area', 'centroid', 'slice', 'intensity_mean']
    cells = measure.regionprops_table(seg_lbl, intensity_image=imgs, properties=properties)
    cells = pd.DataFrame(cells, index=cells['label'])
    return cells

def neighborhood_of_cells(lst_of_slice_tuples, img_length, radius=250, block_side_len=128):
    """Calculates the neighborhood of cells.

    Parameters
    ----------
    lst_of_slice_tuples : list
        List of slice tuples.
    img_length : int
        Length of image.
    radius : int, optional
        Radius of neighborhood in pixels. The default is 250.
    block_side_len : int, optional
        Side length of blocks in pixels. The default is 128.
        
    Returns
    -------
    sl_arr_3d : ndarray
        Array of slice tuples.
    """
    sl_arr = [np.array([[sl[0].start, sl[0].stop], [sl[1].start, sl[1].stop]]) for sl in lst_of_slice_tuples]
    sl_arr_3d = np.dstack(sl_arr)
    sl_arr_3d[:, 0, :] = np.max(np.dstack([sl_arr_3d[:, 0, :] - radius, np.zeros(sl_arr_3d.shape[1:])]), axis=2)
    sl_arr_3d[:, 1, :] = np.min(np.dstack([sl_arr_3d[:, 1, :] + radius, np.full((sl_arr_3d.shape[1:]), img_length)]), axis=2)
    # convert to block coordinates
    sl_arr_3d[:, 0, :] = sl_arr_3d[:, 0, :] // block_side_len
    sl_arr_3d[:, 1, :] = np.ceil(sl_arr_3d[:, 1, :] / block_side_len)
    return sl_arr_3d

def local_bg_intensity(imgs, seg_bg, cells_slice, block_side_len=128):
    """Calculates the local background intensity for each cell.

    First, the image is divided into blocks of size block_side_len x 
    block_side_len. Then for each block the average intensity of the 
    background pixels in that block are calculated. Furthermore, the number of
    background pixels in each block is stored. Using the location of each cell
    the blocks that are close to each cell are identified and the local
    background intensity of that cell is calculated as the weighted (by the 
    number of background pixels) mean of the average background intensities
    for each time point. The output is a pandas DataFrame with the local 
    background intensity traces for each cell in the rows. The rows are named
    after the cell labels.

    Parameters
    ----------
    imgs : (M, N, C) ndarray
        Image sequence where the last dimension is assumed to be the time 
        dimension.
    seg_bg : (M, N) ndarray
        Segmented and labeled image of the background.
    cells_slice : list
        List of slice tuples.
    block_side_len : int, optional
        Side length of blocks in pixels. The default is 128.
    
    Returns
    -------
    local_bg_traces_df : pandas DataFrame
        Contains the local background intensity for each cell.
    """
    n_row_blocks = imgs.shape[1] // block_side_len # number of blocks in row and column
    tiles_3d = (np.arange((imgs.shape[1]) ** 2) // (block_side_len ** 2)).reshape((-1, block_side_len, block_side_len))
    tiles = np.vstack([np.hstack((tiles_3d[(n_row_blocks * i):(n_row_blocks * (i + 1))])) for i in range(n_row_blocks)])
    tiles = tiles + 1 # add 1 to avoid 0 label, i.e. labels start at 1 
    tiles_and_seg_bg = np.min(np.dstack([tiles, tiles.max() * seg_bg]), axis=2) # set non-background pixels to zero

    # calculate the local background intensity over time, also store the area of each label
    bg_local_intensity = measure.regionprops_table(tiles_and_seg_bg, intensity_image=imgs, 
                                                   properties=['label', 'area', 'intensity_mean'])
    bg_local_intensity = pd.DataFrame(bg_local_intensity)

    # store intensity scaled by each label's area for weighted mean calculation
    bg_int_sum = np.array(bg_local_intensity.loc[:, bg_local_intensity.columns.str.startswith('intensity_mean')] * bg_local_intensity['area'].to_numpy().reshape((-1, 1)))
    sl_arr_3d = neighborhood_of_cells(cells_slice, img_length=imgs.shape[1], radius=250, block_side_len=block_side_len)
    cell_locations_tiles = [np.meshgrid(np.arange(*sl_arr_3d[0, :, i]), np.arange(*sl_arr_3d[1, :, i]), indexing='ij') for i in range(sl_arr_3d.shape[2])]
    cell_tile_inds = [(n_row_blocks * mshgrd[0] + mshgrd[1]).ravel() for mshgrd in cell_locations_tiles]

    # calculate the total number of bacḱground pixels in neighborhood of each cell for weighted mean normalization
    total_numpixels = np.array([np.sum(bg_local_intensity['area'].to_numpy()[cell_tile_inds[i]]) for i in range(len(cell_tile_inds))])
    # calculate the local background intensity for each cell by weighted means of closeby tiles
    local_bg_traces = np.vstack([np.sum(bg_int_sum[cell_tile_inds[i], :], axis=0) for i in range(len(cell_tile_inds))]) / total_numpixels.reshape((-1, 1))
    
    row_names = np.arange(1, local_bg_traces.shape[0] + 1, dtype=np.int64)
    local_bg_traces_df = pd.DataFrame(local_bg_traces, index=row_names)
    return local_bg_traces_df

def traces_minus_bg(seg_props, seg_local_bg_cells):
    """Subtracts background traces from cell traces.

    Parameters
    ----------
    seg_props : pandas DataFrame
        Contains the properties of the segemented cells.
    seg_local_bg_cells : pandas DataFrame
        Contains the local background intensity for each cell.
    
    Returns
    -------
    traces_minus_local_bg : pandas DataFrame
        Contains the traces of the cells after subtracting the local background.
    """
    traces = seg_props.loc[:, seg_props.columns.str.startswith('intensity_mean')]
    n_frames = traces.columns.size
    traces.columns = pd.RangeIndex(start=0, stop=n_frames, step=1)
    # traces.columns = np.arange(0, traces.shape[1]) + 1
    # traces_minus_local_bg = traces.to_numpy() - seg_local_bg_cells.to_numpy()
    # traces_minus_local_bg = pd.DataFrame(traces_minus_local_bg, index=np.arange(traces_minus_local_bg.shape[0]) + 1)
    
    # check if traces and seg_local_bg_cells have the same index and columns,
    # otherwise reset and create Warning that index/columns are reset
    if not np.array_equal(traces.index, seg_local_bg_cells.index):
        if traces.shape[0] != seg_local_bg_cells.shape[0]:
            raise ValueError('traces and seg_local_bg_cells have different number of rows.')
        print('Warning: traces and seg_local_bg_cells have different index names. Index is reset.')
        traces.reset_index(drop=True, inplace=True)
        seg_local_bg_cells.reset_index(drop=True, inplace=True)
    if not np.array_equal(traces.columns, seg_local_bg_cells.columns):
        if traces.shape[1] != seg_local_bg_cells.shape[1]:
            raise ValueError('traces and seg_local_bg_cells have different number of columns.')
        print('Warning: traces and seg_local_bg_cells have different column names. Columns are reset.')
        traces.columns = pd.RangeIndex(start=0, stop=traces.columns.size, step=1)
        seg_local_bg_cells.columns = pd.RangeIndex(start=0, stop=seg_local_bg_cells.columns.size, step=1)
    
    traces_minus_local_bg = traces - seg_local_bg_cells
    return traces_minus_local_bg

# def get_slices(sl_arr_3d):
#     sls = np.transpose(sl_arr_3d, (2, 0, 1))
#     sls = [tuple([slice(sl[0, 0], sl[0, 1]), slice(sl[1, 0], sl[1, 1])]) for sl in sls]
#     return sls