# Add Scalebar Python Package

Description: Python GUI to add scale bar (and other processing features) to images within a selected folder

# Installation
## 1. Download through PyPi
`$ python -m pip install em-add-scalebar`
## 2. Download through Git
`$git clone https://git.mpi-cbg.de/scicomp/bioimage_team/tobias_em_app_scalebar.git`

# Quickstart
**1.** After downloading the package, the user interface can be accessed by running

`python -m add_scalebar`

The following window should appear

<img src = "Images/UserInterface.png" width="500">

**2.** In the window, you can change the following parameters

    1. Input Location - Folder containing images to be processed

    2. Input File extension - Type of images to be processed. All other image types are ignored

    3. Output method - Where to save the images

        - Default Save in Subfolder in parent folder: All new files are saved in a folder at the top level named ImageWithScaleBar
        - Save in Subfolder: A subfolder named ImagesWithScaleBar is created for each folder containing images
        - Save in Same Folder: New images are saved in the same folder as original images 
    
    4. Output file extension - New file extension for saved images

    5. Convert images to 8 Bit

    6. Automatically adjust the contrast of each image

    7. Add Scale Bar to images
    
    8. The font color of the scale bar to be added



**3.** Press start to begin the process

Example resulting image

<img src = "Images/ImageExample.png" width="500">
