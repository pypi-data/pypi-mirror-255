import numpy as np
import bm3d

from skimage import (
    exposure, filters, measure, morphology
)

def average_and_denoise(imgs, frames=slice(120, 280)):
    """Takes a sequence of imgs (3d numpy array), averages over first (time) 
    dimension and denoises the resulting image.
    
    Takes a sequence of images (i.e. a 3d numpy array where the first 
    dimension is assumed to be the time dimension) and averages the images over
    time using the specified frames slice. The average image is then denoised
    using BM3D. The output image is rescaled to (0, 1).

    Parameters
    ----------
    imgs : (P, M, N) ndarray
        Image sequence of P images of sizes M times N.
    frames : slice, optional
        Slice which determines which images are going to be used for the 
        averaging and the following workflow. The default is slice(120, 280)
        and hence assumes that there are at least 280 images in the image 
        sequence.

    Returns
    -------
    img_mean_denoised_scaled : (M, N) ndarray
        Denoised and average image.
    """
    # Average images over time
    img_mean = np.mean(imgs[frames], axis=0)
    # Calculate standard deviation
    img_mean_std = np.std(img_mean)
    # Calculate denoised versions
    img_mean_denoised = bm3d.bm3d(img_mean, sigma_psd=img_mean_std, stage_arg=bm3d.BM3DStages.HARD_THRESHOLDING)
    # scale images to (0, 1)
    img_mean_denoised_scaled = exposure.rescale_intensity(img_mean_denoised, out_range=(0, 1))
    return img_mean_denoised_scaled, img_mean

def clip_and_rescale(img, n_low=20, n_high=30):
    """Clips the maximum value of the image so a certain number of connected
    spots are present in the thresholded image at that maximum value.
    
    Takes a 2d image and clips the value so that between n_low and n_high
    number of connected spots are present in the binary image that results 
    when thresholded with that value. The output image is then again rescaled 
    to (0, 1).

    Parameters
    ----------
    img : (M, N) ndarray
        Image of size M times N.
    n_low : int, optional
        Minimum nuber of connected spots have to be present in the thresholded
        image. The default is 20.
    n_high : int, optional
        Maximum nuber of connected spots have to be present in the thresholded
        image. The default is 30.
        
    Returns
    -------
    clipped : (M, N) ndarray
        Clipped and rescaled image.
    """
    clip_max_low = np.min(img)
    clip_max_high = np.max(img)
    clip_max = clip_max_high
    while True:
        clipped = measure.label(img > clip_max)
        n_clipped = np.max(clipped)
        if n_clipped >= n_low and n_clipped <= n_high:
            break
        elif n_clipped < n_low:
            clip_max_high = clip_max
            clip_max = (clip_max_low + clip_max_high) / 2
        elif n_clipped > n_high:
            clip_max_low = clip_max
            clip_max = (clip_max_low + clip_max_high) / 2
    # alternative
    # clip_max = filters.threshold_mulitotsu(img)[1] 
    clipped = np.minimum(img, clip_max)
    # clipped = np.clip(img, a_min=None, a_max=clip_max)
    return clipped * (1 / clip_max)

# calculate the local background intensity by using the local threshold with a large block_size
def subtract_local_bg(img, offset=-0.01, block_size=401, method='mean', mode='nearest'):
    """Calculates background intensity and subtracts this from input image.
    
    Takes a 2d image and clips the value so that between n_low and n_high
    number of connected spots are present in the binary image that results 
    when thresholded with that value. The output image is then again rescaled 
    to (0, 1). The block size and the offset determine are important parameters
    for this function. The block size should be larger than the sizes of the 
    foreground objects. Furthermore, smaller block sizes assume more 
    heterogenity on the background so that the background estimation is 
    relatively smooth. However, too large block sizes can lead to unsensitive 
    background estimation.

    Parameters
    ----------
    img : (M, N) ndarray
        Image of size M times N.
    offset : float, optional
        Offset value for local thresholding algorithm. The default is -0.01.
    block_size : int, optional
        Block size (window size) for local thresholding algorithm. The block 
        size should be larger than the sizes of the foreground objects. 
        The default is 401.
    method : str, optional
        Method for local thresholding algorithm which is to be applied on the
        local windows. If the method is 'mean' a gaussian filter is applied 
        afterwards to smooth out the estimated background which can have 
        rectangular structure due to the rectangular windows. The default is 
        'mean'.
    mode : str, optional
        Mode for local thresholding algorithm which decides what to do with 
        the edges. The default is 'nearest'.
        
    Returns
    -------
    img_minus_bg : (M, N) ndarray
        Image with background subtracted.
    est_bg : (M, N) ndarray
        Estimated background image.
    """
    if method == 'gaussian':
        est_bg = filters.threshold_local(img, block_size=block_size, offset=offset, method=method, mode=mode)
    elif method == 'mean':
        est_bg = filters.threshold_local(img, block_size=block_size, offset=offset, method=method, mode=mode)
        # smooth mean result (which looks chunky) by gaussian filter with sigma corresponding to covering
        # 99% of the gaussian with with 
        est_bg = filters.gaussian(est_bg, sigma=(block_size - 1) / 8) 
    img_minus_bg = img - est_bg
    # should we clip negative values or just shift up and rescale?
    img_minus_bg = np.maximum(0, img_minus_bg) # takes pointwise maximum to prevent negative values
    return img_minus_bg * (1 / np.max(img_minus_bg)), est_bg

def local_threshold(img, offset_img=-0.01, block_size_img=101, 
                    offset_marker=-0.03, block_size_marker=75, min_size=20):
    """Applies thresholding (locally and globally) to image.
    
    Takes an image and uses local thresholding to distinguish foreground 
    objects from the background where foregroung objects are assumed to be
    brighter than the background. In addition a small global threshold is 
    calculated and joined with the locally thresholded image to ensure that
    in areas with few foreground objects the background is still detected
    reliably which can be difficult using only the local threshold. 
    Furthermore, another local threshold is calculated with a lower offset
    and a smaller block size which should detect only the brighter and
    inner parts of the foreground objects. Finally, objects smaller than
    min_size are removed from the thresholded images.

    Parameters
    ----------
    img : (M, N) ndarray
        Image of size M times N.
    offset_img : float, optional
        Offset value for local thresholding algorithm. The default is -0.01.
    block_size_img : int, optional
        Block size (window size) for local thresholding algorithm. The 
        default is 101.
    offset_marker : float, optional
        Offset value for local thresholding algorithm. The default is -0.03.
    block_size_marker : int, optional
        Block size (window size) for local thresholding algorithm. The 
        default is 75.
    min_size : int, optional
        Minimum size of foreground objects. The default is 20.
        
    Returns
    -------
    local_img_and_low_objrem : (M, N) ndarray
        Binary image with local thresholding and global thresholding applied.
    local_marker_and_low_objrem : (M, N) ndarray
        Binary image with stricter local thresholding and global thresholding 
        applied.
    local_img : (M, N) ndarray
        Binary image with local thresholding applied.
    local_marker : (M, N) ndarray
        Binary image with stricter local thresholding applied.
    low : (M, N) ndarray
        Binary image with global thresholding applied.
    """
    local_img = img > filters.threshold_local(img, offset=offset_img, block_size=block_size_img)
    local_marker = img > filters.threshold_local(img, offset=offset_marker, block_size=block_size_marker)
    low = img > filters.threshold_multiotsu(img, classes=3)[0]

    local_img_and_low = local_img & low
    local_marker_and_low = local_marker & low
    local_img_and_low_objrem = morphology.remove_small_objects(local_img_and_low, min_size=min_size)
    local_marker_and_low_objrem = morphology.remove_small_objects(local_marker_and_low, min_size=min_size)
    return local_img_and_low_objrem, local_marker_and_low_objrem, local_img, local_marker, low

# def hdome(img, h=0.35):
#     image = ndi.gaussian_filter(img, 1)
#     seed_shifted = image - h
#     dilated_shifted = morphology.reconstruction(seed_shifted, mask=image, method='dilation')
#     hdome_scaled = exposure.rescale_intensity(image - dilated_shifted, out_range=(0, 1))
#     return hdome_scaled

# def subtract_whitetophat(img, footprint=morphology.disk(5)):
#     wth = morphology.white_tophat(img.astype(np.uint8), footprint=footprint)
#     return img - wth, wth
