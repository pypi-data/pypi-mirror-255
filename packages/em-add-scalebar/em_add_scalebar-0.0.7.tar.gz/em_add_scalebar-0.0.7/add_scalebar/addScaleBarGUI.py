#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 10:21:32 2024

@author: vega
"""
import os
import glob
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
from skimage.exposure import equalize_hist,rescale_intensity
import aicsimageio
from aicsimageio import AICSImage
from ncempy.io import dm
from microfilm.microplot import microshow
import mrcfile
import json
import argparse
from gooey import Gooey, GooeyParser
from wx.core import wx
plt.rcParams.update({'figure.max_open_warning': 0})
is_dark = wx.SystemSettings.GetAppearance().IsUsingDarkBackground()

bg_color = '#343434' if is_dark else '#eeeeee'
wbg_color = '#262626' if is_dark else '#ffffff'
fg_color = '#eeeeee' if is_dark else '#000000'

item_default = {
    'error_color': '#ea7878',
    'label_color': fg_color,
    'help_color': fg_color,
    'description_color': fg_color,
    'full_width': False,
    'external_validator': {
        'cmd': '',
    }
}

#from message import display_message
def addScale(rMeth,imDir,inFile,outFile,convert_8bit,auto_bright_contrast,sb_color):
    #sb_color = 'white'  # Scale bar color
    #sb_length = 20
    #f_stat.insert(0,'Running...')
    
    if rMeth[0] == '1':
        rDir = imDir+'_scalebar'
        print(rDir)
        if os.path.exists(rDir):
            print('Folder exists')
        else:
            print('Created new folder: ' +rDir)
            os.mkdir(rDir)
                                                    
    # Get list of images in directory and sub folders

    imageInitList = glob.glob(os.path.join(imDir, '**/*' + inFile),
                      recursive=True)
    imageExc = glob.glob(os.path.join(imDir, '**/*' + outFile[:-4]+'*'),
                          recursive=True)
    checkIm = np.setdiff1d(np.array(imageInitList),np.array(imageExc))
    imList = list(checkIm)
    #sb_list = np.concatenate([[1,2,5],np.arange(10,100,10),np.arange(100,1000,50)])
    sb_list = [1,2,5,10,20,50,100,200,500]
    #print(imageInitList)
    # 1 . Load each image
    if not imList:
        print('No images found with selected file extension. Exiting Code')
    for im in imList:
        #Check if readable (tif)
        sb_unit = 'um'
        
        if inFile == '.mrc':
            img_info = mrcfile.open(im)
            image_sb = np.uint16(img_info.data)
            im_name = os.path.split(im)[1][:-4]
            pixel_size = np.around(img_info.voxel_size.y, 3)/10000 #MRC files read in 10^4 micron 
        elif inFile == '.dm3':
            img_info = dm.dmReader(im)
            image_sb = np.uint16(img_info['data'])
            im_name = os.path.split(im)[1][:-4]
            if img_info['pixelUnit'][0] == 'nm':
                pixel_size = img_info['pixelSize'][0]/1000
            else:
                pixel_size = img_info['pixelSize'][0]
        else:
            img_info = AICSImage(im)
            image_file = cv.imreadmulti(im,flags=cv.IMREAD_ANYDEPTH)
            image_sb = image_file[1][0]
            im_name = os.path.split(im)[1][:-4]
            pixel_size = img_info.physical_pixel_sizes.Y
            
        sb_font = 10
        sb_length_init = np.uint(np.round((image_sb.shape[0]*pixel_size)*0.10))
            
        if sb_length_init ==0:
            if inFile == '.mrc':
                pixel_size = np.around(img_info.voxel_size.y, 3)/10
            elif inFile == '.dm3':
                if img_info['pixelUnit'][0]=='nm':
                    pixel_size = img_info['pixelSize'][0]
                else:
                    pixel_size = img_info['pixelSize'][0]*1000
            else:
                pixel_size =img_info.physical_pixel_sizes.Y*1000
                
            sb_length_init = np.uint((image_sb.shape[0]*pixel_size)*0.10)
            sb_unit = 'nm'
        sb_length = sb_list[np.argmin(np.abs(sb_list-sb_length_init))]
        # 2b Contrast, value doesn't seem to be used in original code

        if auto_bright_contrast:
            p1, p98 = np.percentile(image_sb, (1, 98))
            image_sb = rescale_intensity(image_sb,in_range=(p1, p98))
            
        if convert_8bit:
            image_sb=(image_sb - int(np.min(image_sb))) / (np.max(image_sb) - int(np.min(image_sb)))
            image_sb = np.uint8(image_sb*255)
            
        fig = plt.figure(frameon=False)
        axs = plt.axes()
        microim = microshow(
            images=image_sb, unit=sb_unit, scalebar_size_in_units=sb_length,dpi=400,
            scalebar_unit_per_pix=pixel_size, scalebar_font_size=sb_font,
            scalebar_color=sb_color,ax=axs,scalebar_thickness=0.01)
        if inFile == '.mrc':
            axs.invert_yaxis()
        # Save new image
        if rMeth[0] == '2':
            subFolder = '_scalebar'
            rDir = os.path.split(im)[0]+subFolder
            if os.path.exists(rDir):
                print('')
            else:
                print('Created new folder')
                os.mkdir(rDir)
        elif rMeth[0] == '3':
            rDir = os.path.split(im)[0]

        plt.savefig(os.path.join(rDir, im_name+outFile),
                        bbox_inches='tight', pad_inches=0, dpi=400)
        plt.close()
        print(im_name+' finished')
    #f_stat.insert(0,'Finished') 

@Gooey(program_name='Add Scale Bar',
        terminal_panel_color=bg_color,
        terminal_font_color=fg_color,
        body_bg_color=bg_color,
        header_bg_color=wbg_color,
        footer_bg_color=bg_color,
        sidebar_bg_color=bg_color)
def main():
    stored_args = {}
    cDir = os.getcwd()
    # get the script name without the extension & use it to build up
    # the json filename
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    args_file = "{}-args.json".format(script_name)
    # Read in the prior arguments as a dictionary
    if os.path.isfile(args_file):
        with open(args_file) as data_file:
            stored_args = json.load(data_file)
    else:
        stored_args = {'Input_location': cDir,
                       'Input_file_extenstion': '.tif',
                       'Output_method':"1.[Default] Save in new Parent Folder",
                       'Output_file_extension':".scalebar.tif"
                       }
    settings_msg = 'Progam adds scale bar to all images within folder'
    parser = GooeyParser(description=settings_msg)
    
    group1 = parser.add_argument_group('Input Parameters')
    dirDef = os.getcwd()
    group1.add_argument('Input_location', help="location of images to process", widget='DirChooser',
                        default= stored_args.get('Input_location'),
                        gooey_options={'default_dir': stored_args.get('Input_location'),
                                        'default_path': stored_args.get('Input_location')})
    group1.add_argument('Input_file_extenstion', action='store',default=stored_args.get('Input_file_extenstion'))
    group1.add_argument('Output_method', help="select how processed images are saved", widget='Dropdown'
                        ,default = stored_args.get('Output_method')
                        ,choices=["1.[Default] Save in new Parent Folder","2. Save in new Subfolders","3. Save in Same Folder"])
    group1.add_argument('Output_file_extension', widget='Dropdown'
                        ,default = stored_args.get('Output_file_extension')
                        ,choices=[".scalebar.tif",".scalebar.jpg",".scalebar.png"])
    #group1.add_argument('Output_file_extenstion', action='store',default='.scalebar.tif')

    # group2 = parser.add_argument_group('Function Options')
    group1.add_argument('--Convert_to_8_bit', default =True, action='store_true')
    group1.add_argument('--Auto_Contrast_Enhance', default =True, action='store_true')
    #group1.add_argument('--Add_Scale_Bar', default =True, action='store_true')
    group1.add_argument('Font_color', widget='Dropdown',default='black'
                        ,choices=['black','white','yellow','red'])
    args=parser.parse_args()
    with open(args_file, 'w') as data_file:
        # Using vars(args) returns the data as a dictionary
        json.dump(vars(args), data_file, indent=1)
    #print(args)
    addScale(args.Output_method,args.Input_location,args.Input_file_extenstion,
             args.Output_file_extension,args.Convert_to_8_bit,
             args.Auto_Contrast_Enhance,args.Font_color)
   #display_message()
    
#fun(arg)
if __name__ == '__main__':
    main()
    
   