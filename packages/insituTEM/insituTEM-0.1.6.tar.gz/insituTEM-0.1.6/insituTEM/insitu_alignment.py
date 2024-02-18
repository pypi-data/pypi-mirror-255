# -*- coding: utf-8 -*-
"""
in-situ TEM Toolbox - Movie alignment 

Assembles of functions related to movie alignment

Example:
    
    import insitu_alignment as Al
    Al.get_matrix()

Created on Tue Jun 11 17:22:45 2019
By: Michael and Meng
"""


import numpy as np
import csv
import cv2
from skimage import io #package for TIFF stack reading
import tifffile
from scipy import signal
from tqdm import tqdm




def get_path():
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename #Tkinter will provide UI for file selection
    '''
    Retrieves a path via gui
    '''
    Tk().withdraw() 
    # we don't want a full GUI, so keep the root window from appearing
    path = askopenfilename() 
    # show an "Open" dialog box and return the path to the selected file
    return path

def get_matrix(csvpath = None):
    '''
    Reads a csvfile and pulls the dx and dy data
    '''
    if csvpath == None:    
        csvpath = get_path()
        print('''
=============================================================================
Please choose the csv you want to use
              ''')
    with open(csvpath) as csvfile:
        print("\nreading csv\n")
        readcsv = csv.reader(csvfile, delimiter=',')
        dx = [] 
        dy = []
        for row in readcsv:
            dx.append(float(row[1]))
            dy.append(float(row[2]))
        #Currently only works if the csv is saved without headers
    return dx, dy, csvpath


def Adaptive_template_match(path, NOF, csvout=True, TMout=True, TMdenoise=True, TMdenoise_window=5,extend=True, bg = 150):
    '''
    Function to produce adaptive template matching on tiff image stack based on ROI selection
    input: 
        path: image path for grayscale Tiff stack
        NOF: number of frames for template to grow
        csvout: whether to write the translation matrix
        TMout: whether to write the template match found feature
        TMdenoise: whether to denoise the measured matrix to remove sudden change
        TMdenoise_window: window size for TMdenoise
        bg: background color (0-255)
        extend: whether to extend the image for the translation (avoid crop)
    
    output: 
        Translated  image stack
        Csv file of translation matrix
        Captured ROI location

    Write by Meng Li (mona.mengli@gmail.com) 2024.02.06
    '''
    import cv2
    import numpy as np
    from matplotlib import pyplot as plt
    import tifffile
    import easygui
    import tqdm
    import insitu_IO as IO
    import insitu_alignment as AL
 
    ###############################################################
    ## 1. Inital settings 

    stack = tifffile.imread(path)
    nFrames, h,w = stack.shape
    
    TM = np.zeros((nFrames,3))#frame, TX,TY,max_val
    pathout3 = path[:-4]+'_TM.csv'
    pathout2 = path[:-4]+'_TM.tif'
    
    ################################################################
    #2. Open fr0 and select ROI for template matching
    img = stack[0]
    ## Select ROI for template matching
    r = cv2.selectROI("Select ROI, press ENTER to confirm",img,fromCenter=False,showCrosshair=False)
    cv2.destroyWindow("Select ROI, press ENTER to confirm")
    # Crop image
    template = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]#opencv coordinate: Y,x , from upper left corner of the image 
    # Display cropped image
    cv2.imshow("Template, press ENTER to confirm", template)
    cv2.waitKey(0)
    cv2.destroyWindow("Template, press ENTER to confirm")
    
    
    
    # ################################################################
    #3. Apply template to template matching
    meth='cv2.TM_CCOEFF_NORMED'
    method = eval(meth)
    w, h = template.shape[::-1]
    
    for i in tqdm.tqdm(range(nFrames)):
        fr=stack[i]
        # Apply template Matching
        res = cv2.matchTemplate(fr,template,method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = max_loc
        TM[i,0]=i
        TM[i,1]=top_left[0]
        TM[i,2]=top_left[1]
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv2.rectangle(fr,top_left, bottom_right, 255, 2)
        # plt.imshow(fr,cmap = 'gray')
        # plt.title('Frame' +str(i)+'  Detected Point')
        if i%NOF==NOF-1:
            template = fr[int(top_left[1]):int(top_left[1] + h), int(top_left[0]):int(top_left[0] + w)]#opencv coordinate: Y,x , from upper left corner of the image 
        if TMout==True: 
            if i == 0:            
                tifffile.imwrite(pathout2,fr, append=False,bigtiff=True)
            else:            
                # tiffile.imsave(pathout2,fr, append=True,bigtiff=True)
                tifffile.imwrite(pathout2,fr, append=True,bigtiff=True)
    
    
    TM[:,1]=TM[0,1]-TM[:,1]
    TM[:,2]=TM[0,2]-TM[:,2]
    
    # ################################################################
    #4. Apply TM to movie
    if TMdenoise==True: 
        #Get average to minimize total movement
        TM=AL.denoiseTM(TM,TMdenoise_window)
        Mx=int(np.mean(TM[:,1]))
        My=int(np.mean(TM[:,2]))
        TM[:,1]=TM[:,1]-Mx
        TM[:,2]=TM[:,2]-My
    
    print("------------------------------------------")
    print("Saving files~")   
    plt.plot(TM[:,0],TM[:,1],'b',TM[:,0],TM[:,2],'r')

    if csvout==True:
        IO.writeCSV(pathout3,TM,fmt='%1.1d')
    
    AL.TranslateStack(path,TM,bg=bg, extend = extend)
    print("Adaptive template matching done!")  
    plt.show()

    
def TranslateStack(movie_path,matrix,bg=150,extend=True):
    '''
    function to apply translation data from a csv
    input: tif stack, matrix[index, tx,ty], background color, extend: whether extend the original image
    output: translated tiff stack
    '''
#    print('''
#=============================================================================
#Please choose the tiff stack you want to translate
#              ''')
#    movie_path = get_path()
    movie_pathout = movie_path[:-4]+'_TF.tif'
    #TS to indicate translated stack
    img = tifffile.imread(movie_path)
    #produces a 3d matrix of nframes, height, width
    nframes, height, width =  img.shape
#    dx, dy, csv_path = get_matrix(csv_path)
    temparray = np.zeros((width, height))

    if extend ==True:
        right= int(abs(max(matrix[:,1])))
        left= int(abs(min(matrix[:,1])))
        top = int(abs(min(matrix[:,2])))
        bottom = int(abs(max(matrix[:,2])))
    else:
        right=0
        left=0
        top=0
        bottom= 0
    height = height+top+bottom
    width = width+left+right
    
    #2d matrix flipped order of width and height to work with warpaffine method
    print("\nApplying translation to stack\n")
    with tifffile.TiffWriter(movie_pathout) as tif:

        for num in tqdm(range(nframes)):
            temparray = img[num,:,:]
            TM= np.float32([[1,0,matrix[num,1]],[0,1,matrix[num,2]]])
            #Generates the translation matrix from the dx dy data
    
                
            extend_img = cv2.copyMakeBorder(temparray, top, bottom, left, right, cv2.BORDER_CONSTANT, value=bg)
            translated_img = cv2.warpAffine(extend_img,TM,(width,height),borderValue =bg)#fill with gray
            #Generates an image translated by dx and dy
            # if num == 0:                    
            #     tifffile.imwrite(movie_pathout, translated_img, append=False, bigtiff=True)
            #     #Overrides any previous files saved to the same path
            # else:
            #     tifffile.imwrite(movie_pathout, translated_img, append=True, bigtiff=True)
            #     #appends onto the tiff stack
            tif.write(translated_img, contiguous=True)

            
def denoise(csvpath=None):
    '''
    function to denoise a tranlsation matrix using median filtering
    input: none
    output: denoised translation matrix saved as a csv
    Example:
        path = get_path()
        template_match(path)
        denoise()
        apply_translation()
    '''
    dx, dy, csvpath = get_matrix(csvpath)
    csvpathout = csvpath[:-4]+'_denoise.csv'
    mediandx = signal.medfilt(dx,5)
    mediandy = signal.medfilt(dy,5)
    #Kernel set to 5
    index = np.zeros((len(dx),2))
    for num in range(len(dx)):
        index[num,0] = mediandx[num]
        index[num,1] = mediandy[num]
    np.savetxt(csvpathout, index, fmt = '%1.1d', delimiter=",")
    return index


def denoiseTM(TM,tw=5):
    '''
    function to denoise a tranlsation matrix using median filtering
    input: Translation matrix[i,dX,dY],filter width tw
    output: denoised translation matrix saved as a csv
    Example:
        path = get_path()
        template_match(path)
        denoise()
        apply_translation()
    '''
    # dx, dy, csvpath = get_matrix(csvpath)
    # csvpathout = csvpath[:-4]+'_denoise.csv'
    dx=TM[:,1]
    dy=TM[:,2]
    mediandx = signal.medfilt(dx,tw)
    mediandy = signal.medfilt(dy,tw)
    #Kernel set to 5
    
    index = np.zeros((len(dx),3))
    index[:,0]=TM[:,0]
    for num in range(len(dx)):
        index[num,1] = mediandx[num]
        index[num,2] = mediandy[num]
    # # np.savetxt(csvpathout, index, fmt = '%1.1d', delimiter=",")
    return index
    
def stackreg(path = None):
    '''
    Applies SIFT translation to the image stack provided and prints the translation matrix to a csvfile
    input: 
    output: Translation matrix saved as a csv and the csv path
    Example:
        path = get_path()
        stackreg(path)
        apply_translation()
    '''
    from pystackreg import StackReg
    if path == None:
        path = get_path()
    csvpathout = path[:-4] + "_SR.csv"
    img = io.imread(path) # 3 dimensions : frames x width x height
    nframes, height, width = img.shape
    sr = StackReg(StackReg.TRANSLATION)
    TM = sr.register_stack(img, reference = 'previous', verbose = True)
    #Previous seems to be the best for our purposes
    #The ImageJ plugin I believe uses previous
    '''
    reference = (string, one of ['previous', 'first', 'mean']) –
    ‘previous’: Aligns each frame (image) to its previous frame in the stack
    ’first:’ Aligns each frame (image) to the first frame in the stack - if n_frames is > 1, then each frame is aligned to the mean of the first n_frames of the stack
    ’mean’: Aligns each frame (image) to the average of all images in the stack
    '''
    TempTM = np.zeros((nframes, 2))
    for num in range(nframes):
        TempTM[num,0] = TM [num, 0, 2]
        TempTM[num,1] = TM [num, 1, 2]   
    np.savetxt(csvpathout, TempTM, fmt = '%1.1d', delimiter=",")
    return csvpathout
    
def get_roi(imgpath):
    '''
    function to allow roi selection with a gui
    input: image path
    output: region of interest (x,y,w,h), template image, and full image
    '''
    im = cv2.imread(imgpath)
    #only reads the first image in the Tiff stack 
    # Select ROI
    roi = cv2.selectROI(im, False, False)
    img = io.imread(imgpath)
    templ = img[0, int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    cv2.imshow("Image", templ)
    #Displays the cropped image
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #closes the cropped image
    return roi, templ, img

def template_match(imgpath, w=24):
    '''
    function to produce a translation matrix based off of template matching
    input: image path
    output: csv with dx and dy in separate columns
    example:
        path = get_path()
        template_match(path)
        denoise()
        apply_translation()
    '''
    import insitu_IO as IO
    from skimage.feature import match_template
    csvpathout = imgpath[:-4] + "_TMatch.csv"
    #Gets the image path
    r, templ, img = get_roi(imgpath)
    #w is the number of pixels around the template that the program will search
    tiffstack = img[:, int(r[1])-w:int(r[1]+r[3])+w, int(r[0])-w:int(r[0]+r[2])+w]
    #Tiffstack is the region that will be searched for matching points
    x = np.zeros((tiffstack.shape[0]), dtype = "int")
    y = np.zeros(tiffstack.shape[0], dtype = "int")
    #Generate numpy arrays to hold the x and y coordinates of the matching points
    iterate = tqdm(range(tiffstack.shape[0]))
    for num in iterate:
        result = match_template(tiffstack[num], templ)
        ij = np.unravel_index(np.argmax(result), result.shape)
        x[num], y[num] = ij[::-1]
    dx = x - w
    dy = y - w
    TM = np.zeros((tiffstack.shape[0],2), dtype='int')
    for num in iterate:
        TM[num,0] = dx[num]
        TM[num,1] = dy[num]
    IO.writeCSV(csvpathout,TM)