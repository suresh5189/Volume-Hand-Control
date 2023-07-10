for id,lms in enumerate(myHand.landmark):
                # print(id,lms)
                h,w,c = img.shape
                cx,cy = int(lms.x*w),int(lms.y*h)
                # print(id,cx,cy)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id,cx,cy])
                if draw:
                    cv2.circle(img,(cx,cy)