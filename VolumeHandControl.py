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

detector = htm.handDetection(detectionCon=0.7)


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


while True:
    success, img = cap.read()
    
    #Find Hand 
    img = detector.findhands(img)
    lmList = detector.findPosition(img,draw=False)
    if len(lmList) != 0:
        # print(lmList[4],lmList[8])
    
        x1,y1 = lmList[4][1],lmList[4][2]
        x2,y2 = lmList[8][1],lmList[8][2]
        cx,cy = (x1+x2)//2,(y1+y2)//2
        
        cv2.circle(img,(x1,y1),10,(0,0,255),cv2.FILLED)
        cv2.circle(img,(x2,y2),10,(0,0,255),cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),3)
        cv2.circle(img,(cx,cy),8,(0,0,255),cv2.FILLED)
        
        length = math.hypot(x2-x1,y2-y1)
        # print(length)
        
        # Hand Range 50-300
        # Volume Range -65 - 0
        
        vol = np.interp(length,[50,300],[min_Volume,max_Volume])
        volumeBar = np.interp(length,[50,300],[400,150])
        volumePercentage = np.interp(length,[50,300],[0,100])
        # print(vol)
        volume.SetMasterVolumeLevel(vol, None)
        
        if length<50:
            cv2.circle(img,(cx,cy),8,(255,0,255),cv2.FILLED)
            
        cv2.rectangle(img,(50,150),(85,400),(0,0,255),3)
        cv2.rectangle(img,(50,int(volumeBar)),(85,400),(0,255,0),cv2.FILLED)
        cv2.putText(img,f'Volume:{int(volumePercentage)}%',(40,450),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),3)
            
    
    currentTime = time.time()
    FPS = 1/(currentTime-previousTime)
    previousTime = currentTime
    
    cv2.putText(img,f'FPS:{int(FPS)}',(40,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,0),3)
    
    cv2.imshow("Output",img)
    cv2.waitKey(1)