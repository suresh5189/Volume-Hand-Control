import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# ----------------------------------------------------------------
widthCamera, heightCamera = 1280, 720
# ----------------------------------------------------------------

cap = cv2.VideoCapture(0)
cap.set(3,widthCamera)
cap.set(4,heightCamera)
previousTime = 0

detector = htm.handDetection(detectionCon=0.7,maxHands=1)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volumeRange = volume.GetVolumeRange()
min_Volume = volumeRange[0]
max_Volume = volumeRange[1]
volumeBar = 400
vol = 0
volumePercentage = 0
area = 0
colorVolume = (255,0,0)


while True:
    success, img = cap.read()
    
    #Find Hand 
    img = detector.findhands(img)
    lmList,bbox = detector.findPosition(img,draw=True)
    if len(lmList) != 0:
        print(lmList[4],lmList[8])
        
        # Filter based on Size
        area = (bbox[2]-bbox[0])*(bbox[3]-bbox[1])//100
        # print(area)
        
        if 250<area<1000:
            
            # Find Distance between Index and Thumb
            length, img, lineInfo = detector.findDistance(4,8,img)
            # print(length)
            
            # Convert Volume
            volumeBar = np.interp(length,[50,200],[400,150])
            volumePercentage = np.interp(length,[50,200],[0,100])
            
            # Reduce Resolution to make it smoother
            smoothness = 2 #increment of volume by 2
            volumePercentage = smoothness*round(volumePercentage/smoothness)         
               
            # Check fingers up
            fingers = detector.fingersUp()
            # print(fingers)
            
            # If Pinky is down set Volume 
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volumePercentage/100,None)
                cv2.circle(img,(lineInfo[4],lineInfo[5]),8,(255,0,255),cv2.FILLED)
                colorVolume = (0,255,0)
            else:
                colorVolume = (255,0,0)
            
    
    # Drawings    
    cv2.rectangle(img,(50,150),(85,400),(0,0,255),3)
    cv2.rectangle(img,(50,int(volumeBar)),(85,400),(0,255,0),cv2.FILLED)
    cv2.putText(img,f'Volume:{int(volumePercentage)}%',(40,450),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),3)
    currentVolume = int(volume.GetMasterVolumeLevelScalar()*100)    
    cv2.putText(img,f'Volume Set:{int(currentVolume)}',(40,500),cv2.FONT_HERSHEY_COMPLEX,1,colorVolume,3)
    # Frame Rate
    currentTime = time.time()
    FPS = 1/(currentTime-previousTime)
    previousTime = currentTime
    
    cv2.putText(img,f'FPS:{int(FPS)}',(40,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),3)
    
    cv2.imshow("Output",img)
    cv2.waitKey(1)