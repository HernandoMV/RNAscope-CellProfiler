# functions to plot cool stuff
#import matplotlib
#import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pandas as pd
from matplotlib import cm

def see_object(obj_number, df, segmented_image,original_image,crop_value):
    #find the coordinates of the object
    coords = df.ix[obj_number][['Location_Center_X', 'Location_Center_Y']]
    x_coord = int(np.asmatrix(coords[[0]].astype(int)))
    y_coord = int(np.asmatrix(coords[[1]].astype(int)))
    #find the cropping points
    cpx1 = max(0, x_coord - crop_value)
    cpy1 = max(0, y_coord - crop_value)
    cpx2 = min(segmented_image.size[0], x_coord + crop_value)
    cpy2 = min(segmented_image.size[1], y_coord + crop_value)
    #crop images
    seg_im = segmented_image.crop((cpx1, cpy1, cpx2, cpy2))
    ori_im = original_image.crop((cpx1, cpy1, cpx2, cpy2))
    #produce the figure
    new_im = Image.new('RGB', (crop_value*4, crop_value*2))
    new_im.paste(ori_im, (0, 0))
    new_im.paste(seg_im, (crop_value*2, 0))

    return new_im


def plotRabiesCell(seriesData, mainPath, window=30, lut='plasma'):
    # makes a composite plot to show the data and the processed data
    assert isinstance(seriesData, pd.Series), 'Data not pandas series'
    
    # find path name of image eg: 907817_D1_Punish_Slice1_Ipsi_rabies.tif
    Base_name = seriesData[['AnimalID', 'StarterCells', 'cFosCondition', 'SliceNumber', 'BrainSide']].str.cat(sep='_')
    RI_name = Base_name + '_rabies.tif'
    CI_name = Base_name + '_cfos.tif'
    # open
    RI_Image = Image.open(mainPath + 'PulledCroppedImages/' + RI_name).convert('L')
    CI_Image = Image.open(mainPath + 'PulledCroppedImages/' + CI_name).convert('L')
    # crop
    coord_x = int(seriesData['Center_X'])
    coord_y = int(seriesData['Center_Y'])
    RI_Image = cropImage(RI_Image, [coord_x, coord_y], window)
    CI_Image = cropImage(CI_Image, [coord_x, coord_y], window)   
    # recolor
    RI_Image = ChangeLUT(RI_Image, lut)
    CI_Image = ChangeLUT(CI_Image, lut)
    
    # get the processed data
    PI_names = [mainPath + 'CellProfilerOutput/' + Base_name + '_rabies_outlines.tiff',
                mainPath + 'CellProfilerOutput/' + Base_name + '_cFos_outlines_95.tiff',
               mainPath + 'CellProfilerOutput/' + Base_name + '_cFos_outlines_98.tiff',
               mainPath + 'CellProfilerOutput/' + Base_name + '_cFos_outlines_99.tiff']
    ProcessedImage = getProcessedImage(PI_names)
    # crop
    ProcessedImage = cropImage(ProcessedImage, [coord_x, coord_y], window)
    
    # produce the figure
    new_im = Image.new('RGB', (window*6, window*2))
    new_im.paste(RI_Image, (0, 0))
    new_im.paste(CI_Image, (window*2, 0))
    new_im.paste(ProcessedImage, (window*4, 0))
    
    # resize
    new_im = new_im.resize((300, 100), Image.ANTIALIAS)
    
    #return
    return new_im


def cropImage(im, coords, crop_value):
    #find the coordinates of the object
    x_coord = int(coords[0])
    y_coord = int(coords[1])
    #find the cropping points
    cpx1 = max(0, x_coord - crop_value)
    cpy1 = max(0, y_coord - crop_value)
    cpx2 = min(im.size[0], x_coord + crop_value)
    cpy2 = min(im.size[1], y_coord + crop_value)
    #crop images
    croppedIm = im.crop((cpx1, cpy1, cpx2, cpy2))
    return croppedIm


def ChangeLUT(im, lut):
    lut = cm.get_cmap(lut)
    im = np.array(im)
    im = lut(im)
    im = np.uint8(im * 255)
    im = Image.fromarray(im)
    return im


def getProcessedImage(pathsToImages):
    # reads a list of 4 images (white, r, g, b), and overlaps them
    w = np.asarray(Image.open(pathsToImages[0]).convert('L'), dtype='uint8')
    r = np.asarray(Image.open(pathsToImages[1]).convert('L'), dtype='uint8')
    g = np.asarray(Image.open(pathsToImages[2]).convert('L'), dtype='uint8')
    b = np.asarray(Image.open(pathsToImages[3]).convert('L'), dtype='uint8')
    # Merge channels
    im1 = np.stack((w, w, w), axis=2).astype('uint8')
    im2 = np.stack((r, g, b), axis=2).astype('uint8')
    # add them
    out_im = Image.fromarray(im1 + im2)

    return out_im

