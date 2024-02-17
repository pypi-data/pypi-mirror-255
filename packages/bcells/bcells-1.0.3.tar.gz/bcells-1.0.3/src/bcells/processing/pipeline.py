import os
import nd2
import numpy as np
import pandas as pd
import gc
from datetime import datetime

# import matplotlib
# matplotlib.use('Agg')

from matplotlib import pyplot as plt
plt.switch_backend('Agg')
# from matplotlib import patches # where is this used?

from ..util.load import files_with_ending
from .process import (
    average_and_denoise, clip_and_rescale, subtract_local_bg, local_threshold
)
from ..segmentation.segment import (
    segment, process_segmentation
)
from ..segmentation.extract import (
    seg_properties, local_bg_intensity, traces_minus_bg
)
from .standardization import (
    stand60, keep_greater_than_0_traces,divide_by_abs_mean_before_light
)
from .characteristic_func import (
    peak_time, midpoint_mass_5, midpoint_mass_12, midpoint_mass, midpoint_mass_40, length_shortest_int,length_shortest_int_40
)
from .data_manipulation import (
    create_charac_df, create_charac_trace
)
from .plotting import (
    plot_traces, plot_all_charac, plot_charac_barys
)
from .wasserstein import (
    approx_bary
)
from skimage import color, segmentation, measure

# set file name
def segment_and_extract(path, filename, data_dir, seg_dir):
    """Pipeline function to calculate segmentation and extract traces from 
    image sequence in nd2 file.

    Parameters
    ----------
    path : str
        Path to directory containing the nd2 file.
    filename : str
        Name of the nd2 file to be processed.
    data_dir : str
        Path to directory where the results data should be stored.
    seg_dir : str
        Path to directory where the segmentation images should be stored.

    Returns
    -------
    traces_bg : pandas DataFrame
        Contains the traces of the cells after subtracting the local background.

    Notes
    -----
    Multichannel inputs are scaled with all channel data combined.

    Examples
    --------

    """
    # import nd2 file and prepare for segmentation
    f_path = os.path.join(path, filename)
    imgs = nd2.imread(f_path)
    filename_wo_ending = filename[:-4] # filename.split('.')[0]

    # average images over time and denoise
    denoised, _ = average_and_denoise(imgs, frames=slice(120, 280))

    # could start subprocess here, which already reorders `imgs`? Does this 
    # work and actually save time?

    # clip and rescale image
    clipped = clip_and_rescale(denoised)
    # subtract local background by local thresholding (via local what? mean or gaussian?)
    c_minus_bg, est_bg = subtract_local_bg(clipped, offset = -0.01)
    # local threshold image
    local_thresh_img, local_thresh_markers, local_img, local_marker, low = local_threshold(c_minus_bg)
    # segement this thresholded image
    seg_out = segment(img=local_thresh_img, markers=local_thresh_markers)
    # process segmentation
    seg = process_segmentation(seg_out)
    # calculate cell segmentation properties
    imgs = np.transpose(imgs, (1, 2, 0)) # regionprops_table expects last dimension to be time dimension
    seg_props = seg_properties(seg_lbl=seg, imgs=imgs)
    # calculate local background intensity
    seg_local_bg_cells = local_bg_intensity(imgs=imgs, seg_bg=(seg == 0).astype(np.int8), 
                                            cells_slice=seg_props['slice'])
    # subtract background traces from cell traces
    traces_bg = traces_minus_bg(seg_props, seg_local_bg_cells)

    # store first frame for output before freiing memory by deleting `imgs`
    first_frame = imgs[:, :, 0]
    del imgs

    ### create and store images from segmentation

    # What data should we store?
    # data:
    #   - seg, seg_props, seg_local_bg_cells, traces_bg
    # images:
    #   - first frame
    #   - denoised
    #   - local background
    #   - local threshold
    #   - segmentation (with colors)
    #   - segmentation (with colors and underlay)
    #   - segmentation (with yellow borders and underlay)
    #   - segmentation (with yellow borders and underlay and numbers)

    os.makedirs(data_dir, exist_ok=True) # create directory if does not exist
    os.makedirs(seg_dir, exist_ok=True) # create directory if does not exist

    ### create more directories for storing data
    # directories for data
    seg_img_dir = os.path.join(data_dir, 'seg')
    seg_props_dir = os.path.join(data_dir, 'seg_props')
    local_bg_props_dir = os.path.join(data_dir, 'local_bg_props')
    traces_dir = os.path.join(data_dir, 'traces')
    data_dirs = [seg_img_dir, seg_props_dir, local_bg_props_dir, traces_dir]
    for d in data_dirs:
        os.makedirs(d, exist_ok=True)
    # directories for images
    first_frame_dir = os.path.join(seg_dir, 'first_frame')
    denoised_dir = os.path.join(seg_dir, 'denoised')
    est_bg_dir = os.path.join(seg_dir, 'est_bg')
    local_thresh_img_dir = os.path.join(seg_dir, 'local_thresh')
    local_thresh_markers_dir = os.path.join(seg_dir, 'local_thresh_markers')
    seg_color_dir = os.path.join(seg_dir, 'seg_color')
    seg_boundary_dir = os.path.join(seg_dir, 'seg_boundary')
    seg_boundary_labeled_dir = os.path.join(seg_dir, 'seg_boundary_labeled')
    seg_dirs = [first_frame_dir, denoised_dir, est_bg_dir, local_thresh_img_dir, local_thresh_markers_dir, seg_color_dir, seg_boundary_dir, seg_boundary_labeled_dir]
    for d in seg_dirs:
        os.makedirs(d, exist_ok=True)

    ### store results data
    object_names = ['seg', 'seg_props', 'seg_local_bg_cells', 'traces_bg']
    file_endings = ['.npy', '.pkl', '.pkl', '.pkl']
    file_names = ['_'.join([filename_wo_ending, obj_name]) + end for obj_name, end in zip(object_names, file_endings)]
    paths = [os.path.join(d, file_name) for file_name, d in zip(file_names, data_dirs)]

    np.save(paths[0], seg)
    seg_props.to_pickle(paths[1])
    seg_local_bg_cells.to_pickle(paths[2])
    traces_bg.to_pickle(paths[3])

    # delete data which is not used anymore
    del seg_props, seg_local_bg_cells

    ### store images from segmentation process
    imgs_black_and_white = [first_frame, denoised, est_bg, local_thresh_img, local_thresh_markers]
    imgs_file_name = ['first_frame', 'denoised', 'estimated_background', 'local_threshold_1', 'local_threshold_2']
    imgs_title = ['First frame of image sequence', 'Denoised image', 'Estimated background', 'Local threshold 1', 'Local threshold 2']

    k = 0
    for img, img_file_name, img_title in zip(imgs_black_and_white, imgs_file_name, imgs_title):
        # create plot and store plot
        path = os.path.join(seg_dirs[k], '_'.join([filename_wo_ending, img_file_name]) + '.png')
        k += 1
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        ax.imshow(img, cmap='gray')
        ax.axis('off')
        ax.set_title(img_title)
        fig.savefig(path, bbox_inches='tight')
        plt.close(fig)

    # plot segmentation results
    seg_color = color.label2rgb(seg, bg_label=0)
    seg_boundary = segmentation.mark_boundaries(clipped, seg)
    
    path = os.path.join(seg_dirs[k], '_'.join([filename_wo_ending, 'seg_color']) + '.png')
    k += 1
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.imshow(seg_color)
    ax.axis('off')
    ax.set_title('Segmentation')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)

    path = os.path.join(seg_dirs[k], '_'.join([filename_wo_ending, 'seg_boundary']) + '.png')
    k += 1
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.imshow(seg_boundary)
    ax.axis('off')
    ax.set_title('Segmentation with boundaries')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)

    path = os.path.join(seg_dirs[k], '_'.join([filename_wo_ending, 'seg_boundary_labeled']) + '.png')
    k += 1
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(seg_boundary)
    for region in measure.regionprops(seg):
        ax.annotate(region.label, (max(region.centroid[1]-15, 0), region.centroid[0]), fontsize=6.5, c="yellow")
    ax.axis('off')
    ax.set_title('Segmentation (cells labeled)')
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)

    # delete rest of data which has been created
    del imgs_black_and_white, first_frame, denoised, clipped, est_bg, \
        local_img, local_marker, low, local_thresh_img, local_thresh_markers, \
        seg_out, seg, seg_color, seg_boundary

    gc.collect()

    return traces_bg

def process_traces(traces_bg):
    """Calculates standardized traces, characteristic functions and approximate
    barycenter.

    Parameters
    ----------
    traces_bg : pandas DataFrame
        Contains the traces of the cells after subtracting the local background.
    
    Returns
    -------
    traces_stand : pandas DataFrame
        Contains the standardized traces of the cells.
    characs : numpy array
        Contains the characteristic values of the cells.
    app_bary : pandas DataFrame
        Contains the approximate barycenter of the cells.
    """
    traces_bg_np = traces_bg.to_numpy()
    traces_gt_0 = keep_greater_than_0_traces(traces_bg_np)
    traces_stand = stand60(traces_gt_0, x=None, light_on=60, fps=2)
    characteristics = ["peak_time", "midpoint_mass_5", "midpoint_mass_12", "midpoint_mass", "midpoint_mass_40", "length_shortest_int", "length_shortest_int_40"]
    characs = create_charac_df(traces_stand, characteristics, x_mat=None)
    _, bary = approx_bary(traces_stand, method="mean", n=None, fps=2)
    charac_bary = pd.DataFrame(create_charac_trace(bary, characteristics, x=None), index=characteristics).T

    return traces_stand, characs, bary, charac_bary

def pipeline_files(path_to_files_dir, filenames, concs, path_to_output_dir=None):
    """Loads nd2 files and applies the segmentation function and the analysis 
    of the traces.

    This is the main function which should be easy to use for the user. It
    creates a directory containing results of the analysis. Images of the
    segmentations are stored, plots of possibly relevant data is plotted
    and calculated segmentations and traces are stored. The data folder
    contains the following folders seg (segmentation data), seg_props 
    (properties/traces using segmentation), local_bg_props (local background
    traces), traces (traces after subtracting local background) and all_traces
    (contains all traces/characteristics in a pickle file).

    Parameters
    ----------
    path_to_files_dir : str
        Path to directory containing the nd2 files.
    filenames : list of str
        List of names of the nd2 files to be processed.
    concs : list of float
        List of concentrations of the nd2 files to be processed.
    path_to_output_dir : str, optional
        Path to directory where the results should be stored. If None, a new 
        directory is created in `path_to_files_dir`.
    
    Returns
    -------
    True : bool
        Returns True if the function was executed successfully.
    """
    print("Detected {} files:".format(len(filenames)))
    for fname in filenames:
        print(fname)
    
    if path_to_output_dir is None:
        date_and_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_name = '_'.join(["bcells", "output", date_and_time])
        path_to_output_dir = os.path.join(path_to_files_dir, dir_name)
        # check if directory exists
        if os.path.isdir(path_to_output_dir):
            raise Exception("Tried to create output directory with name '" + dir_name + "' but this already exists.")
        else:
            os.makedirs(path_to_output_dir)
    else:
        if os.path.isdir(path_to_output_dir):
            print("Warning: Data might be overwritten since supplied output directory already exists with path\n" + path_to_output_dir)
        os.makedirs(path_to_output_dir, exist_ok=True)

    traces_list = []
    log_0_val_plot = 5e-2
    data_dir = os.path.join(path_to_output_dir, "data") # filenames[i][:-4])
    seg_dir = os.path.join(path_to_output_dir, "seg") # filenames[i][:-4])

    for i in range(len(filenames)):
        print("Processing file {} of {}.".format(i+1, len(filenames)))
        traces_bg = segment_and_extract(path_to_files_dir, filenames[i], data_dir, seg_dir)
        conc = concs[i]

        conc_plot = conc
        if conc_plot == 0:
            conc_plot = log_0_val_plot
        tr_st, charac, app_bary, charac_bary = process_traces(traces_bg)
        charac['conc_plot'] = conc_plot
        charac_bary['conc_plot'] = conc_plot
        traces_list.append({'traces': traces_bg, 'conc': conc, 'conc_plot': conc_plot,'traces_stand': tr_st, 'charac': charac, 'app_bary': app_bary, 'charac_bary': charac_bary})
    
    charac_df_all = pd.concat([elem['charac'] for elem in traces_list], ignore_index=True)
    charac_barys = pd.concat([elem['charac_bary'] for elem in traces_list], ignore_index=True)
    characteristics = []
    for elem in charac_df_all.columns.values.tolist():
        if elem != "conc_plot":
            characteristics.append(elem)

    # store traces_list
    traces_list_file_name = "traces_list.pkl"
    all_traces_dir =  os.path.join(data_dir, 'all_traces')
    os.makedirs(all_traces_dir, exist_ok=True)
    traces_list_path = os.path.join(all_traces_dir, traces_list_file_name)
    pd.to_pickle(traces_list, traces_list_path)

    ### create and store plots
    # create directories for storing plots
    plot_dir = os.path.join(path_to_output_dir, "plot") # filenames[i][:-4])
    plot_traces_dir = os.path.join(plot_dir, "traces")
    plot_charac_dir = os.path.join(plot_dir, "charac")
    plot_traces_stand_dir = os.path.join(plot_traces_dir, "traces_stand")
    plot_traces_with_bary_dir = os.path.join(plot_traces_dir, "traces_with_bary")
    plot_charac_individual_dir = os.path.join(plot_charac_dir, "charac_individual")
    plot_charac_bary_dir = os.path.join(plot_charac_dir, "charac_bary")

    os.makedirs(plot_dir, exist_ok=True)
    os.makedirs(plot_traces_dir, exist_ok=True)
    os.makedirs(plot_charac_dir, exist_ok=True)
    os.makedirs(plot_traces_stand_dir, exist_ok=True)
    os.makedirs(plot_traces_with_bary_dir, exist_ok=True)
    os.makedirs(plot_charac_individual_dir, exist_ok=True)
    os.makedirs(plot_charac_bary_dir, exist_ok=True)
    
    # standardized traces (with standardized barycenter) plot
    for i in range(len(traces_list)):
        conc = traces_list[i]['conc']
        traces_stand = traces_list[i]['traces_stand']
        bary_stand = divide_by_abs_mean_before_light(traces_list[i]['app_bary'])

        # plot traces
        fig, ax = plt.subplots(figsize=(10, 5))
        ax = plot_traces(traces_stand, conc=conc, ax=ax)
        path = os.path.join(plot_traces_stand_dir, 'traces_stand_' + str(conc) + '.png')
        fig.savefig(path, bbox_inches='tight')
        plt.close(fig)

        # with bary
        fig, ax = plt.subplots(figsize=(10, 5))
        ax = plot_traces(traces_stand, conc=conc, bary=bary_stand, ax=ax)
        path = os.path.join(plot_traces_with_bary_dir, 'traces_bary_' + str(conc) + '.png')
        fig.savefig(path, bbox_inches='tight')
        plt.close(fig)

    # concentrations for log plots
    concs_true = [elem['conc'] for elem in traces_list]
    concs_plot = [elem['charac']['conc_plot'].iloc[0] for elem in traces_list]

    # violin plot
    for chr in characteristics:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax = plot_all_charac(dat=charac_df_all, y=chr, concs_true=concs_true, concs_plot=concs_plot, ax=ax)
        path = os.path.join(plot_charac_individual_dir, 'all_' + chr + '.png')
        fig.savefig(path, bbox_inches='tight')
        plt.close(fig)

    # barycenter characteristic plot
    for chr in characteristics:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax = plot_charac_barys(dat=charac_barys, y=chr, concs_true=concs_true, concs_plot=concs_plot, ax=ax)
        path = os.path.join(plot_charac_bary_dir, 'bary_' + chr + '.png')
        fig.savefig(path, bbox_inches='tight')
        plt.close(fig)

    return True