import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def get_slice(zoom):
   return slice(zoom[0][0], zoom[0][1]), slice(zoom[1][0], zoom[1][1])

def save_fig(fig, filename, dir):
    filepath = os.path.join(dir, filename)
    
    # if file exists suffix number and take first which doesn't exist
    if os.path.exists(filepath):
        filename_wo_ext = filename[:-4] # does this always work? yes for .pdf and .png, I guess
        i = 1
        filepath_number = os.path.join(dir, filename[:-4] + str(i) + filename[-4:])
        while os.path.exists(filepath_number):
            i += 1
        filepath = filepath_number

    fig.savefig(filepath, bbox_inches='tight', pad_inches=0.1, dpi=300)
    return None

def zoom_overlay(plot_img, zoom, plot_title="", plt_cmap='gray', save_figure=False, dir=None, filename=None):
    fig, ax = plt.subplots()
    extent = (-0.5, plot_img.shape[0]-0.5, -0.5, plot_img.shape[1]-0.5)
    ax.imshow(plot_img, extent=extent, cmap=plt_cmap)

    # inset axes....
    x1, x2, y1, y2 = zoom[0][0], zoom[0][1], zoom[1][0], zoom[1][1]
    axins = ax.inset_axes(
        [0.5, 0.5, 0.47, 0.47], 
        xlim=(x1, x2), ylim=(y1, y2), xticklabels=[], yticklabels=[])
    axins.imshow(plot_img, extent=extent, cmap=plt_cmap)

    ax.indicate_inset_zoom(axins, edgecolor="black")
    ax.set_axis_off()
    ax.set_title(plot_title)

    # plt.show()
    if save_figure:
        if filename is None:
            filename = plot_title
        filename = filename + '.png'
        save_fig(fig=fig, filename=filename, dir=dir)
    else:
        plt.show()
    return fig, ax

def imshow_grid(plot_imgs, plot_titles=None, nrows=1, figsize=(11, 8), cmap='gray', zoom=None, 
                save_figure=False, filename=None, dir=None, draw_rectangle=False):
    fig, axes = plt.subplots(nrows=nrows, ncols=len(plot_imgs) // nrows, figsize=figsize)
    
    # if zoom is not None, zoom images if draw_rectangle is False, else draw rectangle and don't zoom
    zoom_images = False
    if (not (zoom is None)) & (not draw_rectangle):
        zoom_images = True

    # Create a Rectangle patch
    if not (zoom is None):
        zoom_sl = get_slice(zoom)
        if draw_rectangle:
            rects = []
            zoom_lower = zoom_sl[1], zoom_sl[0]
            for i in range(len(plot_imgs)):
                rects.append(patches.Rectangle(xy = (zoom_lower[0].start, zoom_lower[1].start), 
                                               width = zoom_lower[0].stop - zoom_lower[0].start, 
                                               height=zoom_lower[1].stop - zoom_lower[1].start, 
                                               linewidth=1, edgecolor='r', facecolor='none'))
        
    if len(plot_imgs) > 1:
        ax = axes.ravel()
    else:
        ax = [axes]

    for j in range(len(ax)):
        if zoom_images:
            ax[j].imshow(plot_imgs[j][zoom_sl], cmap=cmap)
        else:
            ax[j].imshow(plot_imgs[j], cmap=cmap)
        if draw_rectangle:
            ax[j].add_patch(rects[j])
            # ax[j].relim()
            # ax[j].autoscale_view()
        if not (plot_titles is None):
            ax[j].set_title(plot_titles[j])
        ax[j].set_axis_off()

    fig.tight_layout()
    
    if save_figure:
        if filename is None:
            filename = plot_titles[0] + '.png'
        if filename[-4:] != '.png':
            filename = filename + '.png'
        save_fig(fig=fig, filename=filename, dir=dir)
        
        plt.clf()
        plt.close() # close figure to save memory
    else:
        plt.show()
    return fig, ax

def save_complete_rectangle_zoom_plots(plot_imgs, plot_titles, zoom, dir, fnames=None, nrows=1):
    plots = ['complete', 'rectangle', 'zoom']
    fnames = ['_'.join([''.join((pt.split(sep=' (')[0]).split()) for pt in plot_titles]) + '_' + plot_type for plot_type in plots]

    zs = [None, zoom, zoom]
    draw_rectangles = [False, True, False]

    for i in range(len(zs)):
        fig, ax = imshow_grid(plot_imgs=plot_imgs, plot_titles=plot_titles, nrows=nrows,
                                    zoom=zs[i], draw_rectangle=draw_rectangles[i],
                                    save_figure=True, dir=dir, filename=fnames[i])
        plt.clf()
        plt.close()
    plt.clf()
    plt.close('all')
    return None

def save_image(img, dir, filename, title=None, figsize=(10, 10), cmap='gray'):
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.imshow(img, cmap=cmap)
    if not (title is None):
        ax.set_title(title)
    ax.set_axis_off()
    fig.tight_layout()

    save_fig(fig=fig, filename=filename, dir=dir)
        
    # is next code stuff good=
    plt.clf() # close figure?
    plt.close() # close figure to save memory
    # fig.close()

    # return True
    
def segmentation_with_borders(seg, color):
    fig = 1
    return fig

def segmentation_with_borders_numbered(seg, color):
    fig = 1
    return fig