##### import libraries
import numpy as np
import pandas as pd
from scipy import ndimage as ndi

# from skimage import data
from skimage import (
    color, segmentation, measure, morphology
)

def segment(img, markers):
    """Takes an image and and a marker image and calculates the watershed
    segmentation.
    
    The marker image is labeled and then used to get seed values for the 
    watershed segmentation. The input image is used transformed into a 
    distance image and additionally used as a mask for the watershed 
    segmentation. 

    Parameters
    ----------
    img : (M, N) ndarray
        Binary image of size M times N.
    markers : (M, N) ndarray
        Binary image of size M times N.

    Returns
    -------
    ws_dist : (M, N) ndarray
        Segmented image.
    """
    img_ws = img
    markers = measure.label(markers)
    mask = img
    #   ws = segmentation.watershed(img_ws, markers=markers,mask=mask)
    ws_dist = segmentation.watershed(-ndi.distance_transform_edt(img_ws), markers=markers, mask=mask)
    return ws_dist

def process_segmentation(ws, expand_lbls_dist=0, min_size=200):
  """Processes the watershed segmentation by removing small objects and
  expanding the labels.
  
  Parameters
  ----------
  ws : (M, N) ndarray
      Segmented image.
  expand_lbls_dist : int, optional
      Distance by which labels are expanded. The default is 0.
  min_size : int, optional
      Minimum size of foreground objects. The default is 200.
  
  Returns
  -------
  seg : (M, N) ndarray
      Processed segmentation image.
  """
  seg_o = morphology.remove_small_objects(ws, min_size=min_size)
  seg_o_r = segmentation.relabel_sequential(seg_o)[0]

  if (expand_lbls_dist > 0):
    seg = segmentation.expand_labels(seg_o_r, distance=expand_lbls_dist)
  else:
    seg = seg_o_r

#   seg_bg = (seg == 0).astype(np.int8)
#   seg_color = color.label2rgb(seg_o_r)
  return seg # , seg_color, seg_bg
