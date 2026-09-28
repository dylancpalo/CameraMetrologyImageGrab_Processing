import imagingcontrol4 as ic4
import sys
import cv2
import numpy as np
import time
import serial
import glob
import os
import cv2 as cv
lowerIntLED = [0, int(1*3+1), int(2*3 + 0), int(4*3 + 1), int(6*3+1), int(7*3 + 0), int(7*3 +2)]
exposure = float(sys.argv[1])
#-----------------------------------------------------------------------
def CombinedImages(OGFileName):
    imArr = []
    Offset = -5
    sortedNames = sorted(glob.glob("%s*"%(OGFileName[:Offset])))
    
    SlashLoc = -1
    for i in range(len(OGFileName)):
        #print(OGFileName[i], "\\")
        if (OGFileName[i]=="\\"):
            SlashLoc=i
            break
    SlashLoc =SlashLoc+1
    Name = OGFileName[SlashLoc:]
    Dir = OGFileName[0:SlashLoc-1]
    CombinedDir = Dir+"C"
    #print(len(OGFileName), SlashLoc, CombinedDir, Dir, Name)
    dummy = 1
    try:
        os.mkdir(CombinedDir)
        #print(f"Directory '{CombinedDir}' created successfully.")
    except FileExistsError:
        dummy=0

    for i in range(len(sortedNames)):
        im = cv.imread(sortedNames[i])
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        imArr.append(imgray)

    #print(imArr[0].shape, imArr[1].shape, imArr[2].shape)
    XLen = imArr[0].shape[1]
    XLenThird = int(XLen/3)
    imMaster = np.hstack((imArr[2][:,0:XLenThird], imArr[1][:,XLenThird:2*XLenThird], imArr[0][:,2*XLenThird:]))
    finalDir_Name = "%s/%s"%(CombinedDir, Name)
    #print(finalDir_Name)

    cv.imwrite("%s"%(finalDir_Name), imMaster)
    return CombinedDir
#-----------------------------------------------------------------------

def LEDAddress(iLED):
    iLED = "%i"%(iLED)
    arduino = serial.Serial(port='COM7', baudrate=9600, timeout=.1)
    arduino.write(bytes(iLED, 'utf-8'))
    time.sleep(0.07)
    data = arduino.readline()
    return


ic4.Library.init()
ordering = np.genfromtxt("ordering.txt", delimiter=", ")
print(ordering)
idealIntensity  = 100
# Create a Grabber object
NImages = int(sys.argv[4])
print("%i Cameras Found"%(len( ic4.DeviceEnum.devices())))
print("Starting Imaging")
def startGrabber(i):
    # Open the first available video capture device
    grabber = ic4.Grabber()
    device_info = ic4.DeviceEnum.devices()[i]
    cam_order = -1
    for iord in range(len(ordering)):
        if (int(device_info.serial)==int(ordering[iord, 1])):
            cam_order = int(ordering[iord, 0])
    #print(cam_order)
    grabber.device_open(device_info)
    return grabber, cam_order, device_info

def SettingsAndStartCam(grabber, thisExposure):
    maxHeight = grabber.device_property_map.get_value_int(ic4.PropId.HEIGHT_MAX)
    maxWidth = grabber.device_property_map.get_value_int(ic4.PropId.WIDTH_MAX)
    
    grabber.device_property_map.set_value(ic4.PropId.WIDTH, maxWidth)
    grabber.device_property_map.set_value(ic4.PropId.HEIGHT, maxHeight)
    grabber.device_property_map.get_value_int(ic4.PropId.WIDTH)
    
        
    # Configure the exposure time to 5ms (5000µs)
    grabber.device_property_map.set_value(ic4.PropId.EXPOSURE_AUTO, "Off")
    grabber.device_property_map.set_value(ic4.PropId.EXPOSURE_TIME, thisExposure)
    
    # Enable GainAuto
    exp = grabber.device_property_map.get_value_float(ic4.PropId.EXPOSURE_TIME)
    #print("exp: ", exp)
    
    grabber.device_property_map.set_value(ic4.PropId.GAIN_AUTO, "Off")
    grabber.device_property_map.set_value(ic4.PropId.GAIN, float(sys.argv[2]))
    gain = grabber.device_property_map.get_value_float(ic4.PropId.GAIN)
    #print("gain: ", gain)
            
    # Create a SnapSink. A SnapSink allows grabbing single images (or image sequences) out of a data stream.
    # Grab a single image out of the data stream.
    sink = ic4.SnapSink()
    grabber.stream_setup(sink, setup_option=ic4.StreamSetupOption.ACQUISITION_START)
    # Setup data stream from the video capture device to the sink and start image acquisition.
    return sink, grabber
for i in range(len( ic4.DeviceEnum.devices())):
    grabber, cam_order, device_info = startGrabber(i)
    if (cam_order>=12):
        continue
    for j in range(3):
        LEDNumber = int(cam_order*3 + j)
        LEDAddress(LEDNumber)
        if (LEDNumber in lowerIntLED):
            thisExposure = exposure*2.
        else:
            thisExposure = exposure
        sink, grabber = SettingsAndStartCam(grabber, thisExposure)
        for k in range(NImages):
            try:
                # Grab a single image out of the data stream.
                image = sink.snap_single(1000)
                # Save the image.
                img_name = "%s/%02d_%i_%i_%i_%02d_%i.bmp"%(sys.argv[3], cam_order, int(device_info.serial), int(sys.argv[1]), int(sys.argv[2]), k, j)
                image.save_as_bmp(img_name)
            except ic4.IC4Exception as ex:
                print(ex.message)
                
        grabber.stream_stop()
LEDAddress(49)  

CombinedDirectory=""
ImageNames = sorted(glob.glob("%s/*0.bmp"%(sys.argv[3])))
for i in range(len(ImageNames)):
    CombinedDirectory = CombinedImages(ImageNames[i])

##--------------------------------------
printTime = 0
makePlots = 0
import time 
import os
initialTime = time.time()
if (printTime):
    t = time.time()
import numpy as np
import cv2 as cv
if (makePlots):
    from matplotlib import pyplot
    import matplotlib
import math
import sys
from scipy.optimize import curve_fit 
import glob



NameCutoff = 17
from ImageAnalysis import *
OptimalBkgMedian =180.
MinBkgLight = 30
Width = 2592
Height = 1944
MaxInt = 255
BkgStem = 55
BkgHalfWidth = 170
if (printTime):
    elapsed = time.time() - t
    print("Startup Time: %f"%(elapsed))
    t = time.time()
#----------main function--------#
#load image
CombinedDirectory = CombinedDirectory +"\\"
sortedNames = sorted(glob.glob("%s*"%(CombinedDirectory)))

for iImg in range(len(sortedNames)):
    if (makePlots):
        matplotlib.rcParams['figure.figsize'] = (10, 3)
        fig, ax = pyplot.subplots(nrows=2, ncols=3,figsize=(20,8))

    print("Analyzing %s"%(sortedNames[iImg]))
    ReducedName = sortedNames[iImg][len(CombinedDirectory):]
    #print(CombinedDirectory, len(CombinedDirectory), "ReducedName", ReducedName)
    im = cv.imread(sortedNames[iImg])
    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

    #centers holds the center values of the circle fits and the radius, N pts
    centers = []
    #list of indices
    finalXIndices = []
    finalYIndices = []
    '''
    circles = cv.HoughCircles(imgray, cv.HOUGH_GRADIENT, 0.1, 800,
                               param1=100, param2=50,
                               minRadius=110, maxRadius=170)
    '''
    circles = cv.HoughCircles(imgray, cv.HOUGH_GRADIENT, 0.1, 800,
                               param1=80, param2=25,
                               minRadius=110, maxRadius=170)
    '''
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv.circle(imgray, center, 1, (255, 255, 255), 3)
            # circle outline
            radius = i[2]
            cv.circle(imgray, center, radius, (255, 0, 255), 1)

    cv.imwrite("ImageOutputs/Circles.jpg", imgray) 
    '''
    if (printTime):
        elapsed = time.time() - t
        print("Import Pic and Initial Circle Estimate Time: %f"%(elapsed))
        t = time.time()

    circles = circles[0, :, :]
    centers = circles[circles[:, 0].argsort()]
    Avg1X = centers[0,0]
    Avg2X = centers[1,0]
    Avg3X = centers[2,0]
    Avg1Y = centers[0,1]
    Avg2Y = centers[1,1]
    Avg3Y = centers[2,1]

    MinX1 = int(Avg1X - BkgHalfWidth)
    MaxX3 = int(Avg3X + BkgHalfWidth)

    #print(Avg1Y, Avg2Y, Avg3Y)
    #print(Avg1X, Avg2X, Avg3X)

    if (MinX1 < 0):
        MinX1 = int(0)
    if (MaxX3 > imgray.shape[1]-1):
        MaxX3 = int(imgray.shape[1]-1)

    MaxX1 = int(Avg1X + BkgHalfWidth)
    MinX3 = int(Avg3X - BkgHalfWidth)

    MaxX2 = int(Avg2X + BkgHalfWidth)
    MinX2 = int(Avg2X - BkgHalfWidth)

    Bkg1 = imgray[int(Avg1Y - BkgHalfWidth):int(Avg1Y + BkgHalfWidth - BkgStem),MinX1:int(Avg1X + BkgHalfWidth)]
    Bkg2 = imgray[int(Avg2Y - BkgHalfWidth):int(Avg2Y + BkgHalfWidth - BkgStem),int(Avg2X - BkgHalfWidth):int(Avg2X + BkgHalfWidth)]
    Bkg3 = imgray[int(Avg3Y - BkgHalfWidth):int(Avg3Y + BkgHalfWidth - BkgStem),int(Avg3X - BkgHalfWidth):MaxX3]
    IndexArrY = np.linspace(0, imgray.shape[0]-1, imgray.shape[0])
    IndexArrX = np.linspace(0, imgray.shape[1]-1, imgray.shape[1])
    IndexMeshX, IndexMeshY = np.meshgrid(IndexArrX, IndexArrY)

    IndexMeshX1 = IndexMeshX[int(Avg1Y - BkgHalfWidth):int(Avg1Y + BkgHalfWidth - BkgStem),MinX1:int(Avg1X + BkgHalfWidth)]
    IndexMeshX2 = IndexMeshX[int(Avg2Y - BkgHalfWidth):int(Avg2Y + BkgHalfWidth - BkgStem),int(Avg2X - BkgHalfWidth):int(Avg2X + BkgHalfWidth)]
    IndexMeshX3 = IndexMeshX[int(Avg3Y - BkgHalfWidth):int(Avg3Y + BkgHalfWidth - BkgStem),int(Avg3X - BkgHalfWidth):MaxX3]

    IndexMeshY1 = IndexMeshY[int(Avg1Y - BkgHalfWidth):int(Avg1Y + BkgHalfWidth - BkgStem),MinX1:int(Avg1X + BkgHalfWidth)]
    IndexMeshY2 = IndexMeshY[int(Avg2Y - BkgHalfWidth):int(Avg2Y + BkgHalfWidth - BkgStem),int(Avg2X - BkgHalfWidth):int(Avg2X + BkgHalfWidth)]
    IndexMeshY3 = IndexMeshY[int(Avg3Y - BkgHalfWidth):int(Avg3Y + BkgHalfWidth - BkgStem),int(Avg3X - BkgHalfWidth):MaxX3]

    IndexMeshX1Cut = IndexMeshX1[np.logical_not(Bkg1 <MinBkgLight)]
    IndexMeshX2Cut = IndexMeshX2[np.logical_not(Bkg2 <MinBkgLight)]
    IndexMeshX3Cut = IndexMeshX3[np.logical_not(Bkg3 <MinBkgLight)]

    IndexMeshY1Cut = IndexMeshY1[np.logical_not(Bkg1 <MinBkgLight)]
    IndexMeshY2Cut = IndexMeshY2[np.logical_not(Bkg2 <MinBkgLight)]
    IndexMeshY3Cut = IndexMeshY3[np.logical_not(Bkg3 <MinBkgLight)]

    Bkg1Cut = Bkg1[np.logical_not(Bkg1 <MinBkgLight)]
    Bkg2Cut = Bkg2[np.logical_not(Bkg2 <MinBkgLight)]
    Bkg3Cut = Bkg3[np.logical_not(Bkg3 <MinBkgLight)]

    Bkg1CutMean = np.median(Bkg1Cut)
    Bkg2CutMean = np.median(Bkg2Cut)
    Bkg3CutMean = np.median(Bkg3Cut)

    #print(Bkg1CutMean, Bkg2CutMean, Bkg3CutMean)

    def func(xy, a, b, c, d, e, f, g, h, i, j): 
        x, y = xy 
        return a + b*x + c*y + d*x**2 + e*y**2 + f*x*y + g*x*x*x + h*y*y*y + i*x*x*y + j*y*y*x


    popt, pcov = curve_fit(func, (IndexMeshX1Cut, IndexMeshY1Cut), Bkg1Cut) 
    MeshZ1 = func((IndexMeshX1.flatten(), IndexMeshY1.flatten()), *popt) 
    MeshZ1=MeshZ1.reshape((int(len(MeshZ1)/(MaxX1-MinX1)), int(MaxX1-MinX1))) 

    popt, pcov = curve_fit(func, (IndexMeshX2Cut, IndexMeshY2Cut), Bkg2Cut) 
    MeshZ2 = func((IndexMeshX2.flatten(), IndexMeshY2.flatten()), *popt) 
    MeshZ2=MeshZ2.reshape((int(len(MeshZ2)/(MaxX2-MinX2)), int(MaxX2-MinX2))) 

    popt, pcov = curve_fit(func, (IndexMeshX3Cut, IndexMeshY3Cut), Bkg3Cut) 
    MeshZ3 = func((IndexMeshX3.flatten(), IndexMeshY3.flatten()), *popt) 
    MeshZ3=MeshZ3.reshape((int(len(MeshZ3)/(MaxX3-MinX3)), int(MaxX3-MinX3)))

    imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
    imgray[int(Avg1Y - BkgHalfWidth):int(Avg1Y + BkgHalfWidth - BkgStem),MinX1:int(Avg1X + BkgHalfWidth)] = \
    imgray[int(Avg1Y - BkgHalfWidth):int(Avg1Y + BkgHalfWidth - BkgStem),MinX1:int(Avg1X + BkgHalfWidth)]*(OptimalBkgMedian/MeshZ1)

    imgray[int(Avg2Y - BkgHalfWidth):int(Avg2Y + BkgHalfWidth - BkgStem),int(Avg2X - BkgHalfWidth):int(Avg2X + BkgHalfWidth)] = \
    imgray[int(Avg2Y - BkgHalfWidth):int(Avg2Y + BkgHalfWidth - BkgStem),int(Avg2X - BkgHalfWidth):int(Avg2X + BkgHalfWidth)]*(OptimalBkgMedian/MeshZ2)

    imgray[int(Avg3Y - BkgHalfWidth):int(Avg3Y + BkgHalfWidth - BkgStem),int(Avg3X - BkgHalfWidth):MaxX3] = \
    imgray[int(Avg3Y - BkgHalfWidth):int(Avg3Y + BkgHalfWidth - BkgStem),int(Avg3X - BkgHalfWidth):MaxX3]*(OptimalBkgMedian/MeshZ3)
    imgray = imgray.astype(np.uint8)
    if (printTime):
        elapsed = time.time() - t
        print("Background Fit Time: %f"%(elapsed))
        t = time.time()

    '''
    #-------------------------------
    #Used to diagnose issue with bkg fit
    #-------------------------------
    def heatmap2d(i, j, arr: np.ndarray):
        im= ax[i, j].imshow(arr, cmap='viridis', vmin=80, vmax=250)
        colorbar = fig.colorbar(im)
        #pyplot.colorbar()
        #pyplot.clim(130, 255)

    heatmap2d(0, 0, Bkg1)
    heatmap2d(1, 0, Bkg2)
    heatmap2d(2, 0, Bkg3)
    heatmap2d(0, 1, MeshZ1)
    heatmap2d(1, 1, MeshZ2)
    heatmap2d(2, 1, MeshZ3)
    heatmap2d(0, 2, imgray[int(Avg1Y - BkgHalfWidth):int(Avg1Y + BkgHalfWidth - BkgStem),MinX1:int(Avg1X + BkgHalfWidth)])
    heatmap2d(1, 2, imgray[int(Avg2Y - BkgHalfWidth):int(Avg2Y + BkgHalfWidth - BkgStem),int(Avg2X - BkgHalfWidth):int(Avg2X + BkgHalfWidth)])
    heatmap2d(2, 2, imgray[int(Avg3Y - BkgHalfWidth):int(Avg3Y + BkgHalfWidth - BkgStem),int(Avg3X - BkgHalfWidth):MaxX3])
    pyplot.show()

    pyplot.clf()
    fig, ax = pyplot.subplots(nrows=3, ncols=1,figsize=(8,8))
    ax[0].hist(Bkg1.flatten(), np.linspace(MinBkgLight, 255, 255-MinBkgLight), label="Median: %.2f"%(np.median(Bkg1)))
    ax[1].hist(Bkg2.flatten(), np.linspace(MinBkgLight, 255, 255-MinBkgLight), label="Median: %.2f"%(np.median(Bkg2)))
    ax[2].hist(Bkg3.flatten(), np.linspace(MinBkgLight, 255, 255-MinBkgLight), label="Median: %.2f"%(np.median(Bkg3)))
    pyplot.show()
    '''

    if (makePlots):
        cv.imwrite("ImageOutputs/LightCorrected.bmp", imgray)
    centersHough = centers
    centers = []
    imgrayFresh = imgray#cv.cvtColor(im, cv.COLOR_BGR2GRAY) #make black and white
    ret, thresh = cv.threshold(imgray, thresholds, maxPixelIntensity, 0) #make threshold image
    if (makePlots):
        cv.imwrite("ImageOutputs/Threshold.jpg", thresh) 
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) #grab contours


    c_select = []
    for c in contours:
        area = cv.contourArea(c)
        #x,y,w,h = cv.boundingRect(c)
        #rect_area = w*h
        #extent = float(area)/rect_area
        if (area < 2000):
            continue
        c_select.append(c)
    zero = np.zeros(im.shape)
    #if (makePlots):
    #   cv.drawContours(imgrayFresh, c_select, -1, (0,maxPixelIntensity,0), 1)
    #   cv.imwrite("ImageOutputs/AllContourOnImage.jpg", imgrayFresh) 
    cv.drawContours(zero, c_select, -1, (0,maxPixelIntensity,0), 1)
    if (makePlots):
        cv.imwrite("ImageOutputs/AllContoursOnBlack.jpg", zero) 
    pts = np.where(zero == maxPixelIntensity)
    pts = np.vstack((pts[0], pts[1])).T
    #draw all contours on the image and on a black image
    contour = np.sum(zero, axis=2)
    ToolingBalls = FilterPixelsLightHough(centersHough, pts, makePlots) #remove bad pixels e.g. stem, edge effects
    if (printTime):
        elapsed = time.time() - t
        print("Process Contour Time: %f"%(elapsed))
        t = time.time()
    #loop over arrays of pixels
    #loop over the three balls 
    for index in range(len(ToolingBalls)):
        thisindices = np.array(ToolingBalls[index])
        #dont bother if there are no pixels
        if (len(thisindices)<10):
            continue
        x = thisindices[:,0]
        y = thisindices[:,1]
        #fit (chi2 again)
        xc_2, yc_2, R_2, xprime, yprime = Fitter1(thisindices, [centersHough[index, 1], centersHough[index, 0], centersHough[index, 2]], x, y, 0)
        #clean up based on residuals, tighter cut
        thisindices= RemoveOutliers(thisindices, ResThreshold2, x-xprime, y-yprime, 1)
        x = thisindices[:,0]
        y = thisindices[:,1]
        if (len(thisindices)<10):
            continue
        #final fit chi2
        xc_2, yc_2, R_2, xprime, yprime = Fitter1(thisindices, [xc_2, yc_2, R_2], x, y, 1)
        alreadyPassed = 0
        #verify you aren't just grabbing the same contour
        for icent in range(len(centers)):
            if (abs(centers[icent][0]-yc_2) < RequiredDistanceAwayFromFoundContour and abs(centers[icent][1]-xc_2) < RequiredDistanceAwayFromFoundContour):
                alreadyPassed=1
        
        #if there is a reasonable number of pixels, and it isn't the same contour, and the ratio of pixels to the radius is reasonable, accept!
        #print("%.2f, %.2f, %.2f, %.2f, %.2f"%(xc_2, yc_2, R_2, len(x), len(x)/R_2))
        if (len(x) > NRequiredPixels*0.1 and len(x)/R_2 > PixelsToRadiusSelection*0.1 and  alreadyPassed==0):
            finalXIndices.append(x)
            finalYIndices.append(y)
            centers.append(np.array([yc_2, xc_2, R_2, len(x)]))
            if (makePlots):
                Ri = np.zeros(len(xprime))
                for i in range(len(xprime)):
                    Ri[i] = np.sqrt((x[i]-xc_2)**2 + (y[i]-yc_2)**2)
                plot = ax[0, len(centers)-1].scatter(x, y,
                           linewidths=0, alpha=.5,
                           edgecolor='k',
                           s = 100,
                           c=Ri-R_2)
                ax[1, len(centers)-1].hist(Ri-R_2, np.linspace(-2, 2, 40), label="sig=%.2f [pix]"%(np.sqrt(np.var(Ri-R_2))))
                ax[1, len(centers)-1].set_ylim([0, 100])
                ax[1, len(centers)-1].set_xlim([-1.5, 1.5])
                ax[1, len(centers)-1].legend()
    centers = np.array(centers)
    if (printTime):
        elapsed = time.time() - t
        print("Fit Time: %f"%(elapsed))
        t = time.time()

    print("Found Tooling Balls")
    print("X [pix] ,  Y [pix],  R [pix],  NPix")
    for i in range(len(centers)):
        print("%8.2f, %8.2f, %8.2f, %8.2f"%(centers[i,0], centers[i,1], centers[i,2], centers[i,3]))

    #-------------------------------------------------------------------
    if (len(centers)!=3):
        print("Not Enough Contours!!!! Will Crash!!!!")
    TripletID = int(ReducedName[0:2])
    print(TripletID, ReducedName)
    CAMID = int(ReducedName[3:11])
    NImage = int(ReducedName[-8:-6])

    csvrow = "%i, %i, %i, %.4f, %.4f, %.4f, %.4f, %.4f, %.4f, %4f, %.4f, %.4f, %.4f, %4f, %.4f\n"%(TripletID, CAMID, NImage,
        centers[0,0], centers[0,1], centers[0,2], Bkg1CutMean, \
        centers[1,0], centers[1,1], centers[1,2], Bkg2CutMean, \
        centers[2,0], centers[2,1], centers[2,2], Bkg3CutMean)
    with open("%sCameraCCDR.csv"%(CombinedDirectory),'a') as fd:
        fd.write(csvrow)

    if (makePlots):
        #residual plots for the three tooling balls are now saved
        fig.colorbar(plot, ax=ax.ravel().tolist())
        pyplot.savefig('ImageOutputs/ResidualPlots.jpg', bbox_inches='tight')

    #sort the contours
    centers=centers[centers[:, 0].argsort()]
    if (makePlots):
        #plot the final contours on a black image
        for i in range(len(centers)):
            for j in range(len(finalXIndices[i])):
                imgray[finalXIndices[i][j],finalYIndices[i][j]]=maxPixelIntensity
        cv.imwrite("ImageOutputs/finalContours.jpg", imgray) 
    #xCam = TransformToCameraCoordMech(centers, nTriplet,NameCutoff)
    #FitForCMMTransformation(xCam, nTriplet, NameCutoff)

elapsed = time.time() - initialTime
print("Total Elapsed Time: %.2f s"%(elapsed))

stationID = int(sys.argv[7])
iteration = int(sys.argv[8])
#print(stationID, iteration, TripletID, CAMID)
TotalCamArray = np.genfromtxt("%sCameraCCDR.csv"%(CombinedDirectory), delimiter=", ")
print(TotalCamArray.shape)
AverageCamArray = np.zeros((int(TotalCamArray.shape[0]/4),TotalCamArray.shape[1]))
#print(TotalCamArray)
startingIndex = 0
for i in range(len(AverageCamArray)):
    AverageCamArray[i,:] = (TotalCamArray[startingIndex,:]+TotalCamArray[startingIndex+1,:]+TotalCamArray[startingIndex+2,:]+TotalCamArray[startingIndex+3,:])/4
    startingIndex=startingIndex+4
    csvrow = ""

    #print(AverageCamArray[i,0])
    if (np.in1d(AverageCamArray[i,0], [0,4,8,2,6,10])):
        csvrow = "INSERT INTO met.panelfiducialimages VALUES (%i, %i, %i, %i, %i, %.4f, %.4f, %.4f, %4f, %.4f, %.4f, %.4f, %4f, %.4f, %.4f, %.4f, %.4f);\n"%(\
        stationID, iteration, AverageCamArray[i,0], AverageCamArray[i,1], 0, \
        AverageCamArray[i, 3+ 0*4], AverageCamArray[i, 4+ 0*4], AverageCamArray[i, 5+0*4], AverageCamArray[i, 6+0*4], \
        AverageCamArray[i, 3+ 2*4], AverageCamArray[i, 4+ 2*4], AverageCamArray[i, 5+2*4], AverageCamArray[i, 6+2*4], \
        AverageCamArray[i, 3+ 1*4], AverageCamArray[i, 4+ 1*4], AverageCamArray[i, 5+1*4], AverageCamArray[i, 6+1*4])
    else:
        print(i)
        csvrow = "INSERT INTO met.panelfiducialimages VALUES (%i, %i, %i, %i, %i, %.4f, %.4f, %.4f, %4f, %.4f, %.4f, %.4f, %4f, %.4f, %.4f, %.4f, %.4f);\n"%(\
        stationID, iteration, AverageCamArray[i,0], AverageCamArray[i,1], 0, \
        AverageCamArray[i, 3+ 2*4], AverageCamArray[i, 4+ 2*4], AverageCamArray[i, 5+2*4], AverageCamArray[i, 6+2*4], \
        AverageCamArray[i, 3+ 0*4], AverageCamArray[i, 4+ 0*4], AverageCamArray[i, 5+0*4], AverageCamArray[i, 6+0*4], \
        AverageCamArray[i, 3+ 1*4], AverageCamArray[i, 4+ 1*4], AverageCamArray[i, 5+1*4], AverageCamArray[i, 6+1*4])


    with open('%sAverageCAM.txt'%(CombinedDirectory),'a') as fd:
        fd.write(csvrow)


#transform xCCD-> xCAM using the mech measurements

#use below to fit for the original CMM transformation

#apply the correct CMM transformation to the balls (grabbed from CSV): xCam -> xCMM
#xCMM = applyCMMTransformation(xCam, nTriplet, NameCutoff, 1)
