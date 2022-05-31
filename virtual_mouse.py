import cv2
import numpy as np
import time
import pyautogui
import mediapipe as mp
import math
################################################### CLASS AND FUNCTIONS ################################################

class handDetector():
    def __init__(self, mode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.modelComplex = modelComplexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                              (0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        # Thumb
        if len(self.lmList) != 0:
            if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

            # Fingers
            for id in range(1, 5):

                if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # totalFingers = fingers.count(1)

            return fingers
        else:
            fingers = [0,0,0,0,0]
            return fingers


    def findDistance(self, p1, p2, img, draw=True,r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]


############################################## IMPORTANT VARIABLES #####################################################

widthCam, heightCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
pastTime = 0
pastLocationX, pastLocationY = 0, 0
currentLocationX, currentLocationY = 0, 0

############################################# CAPTURING VIDEO ##########################################################


cap = cv2.VideoCapture(0)
cap.set(3, widthCam)
cap.set(4, heightCam)
detector = handDetector(maxHands=1)
widthScr, heightScr = pyautogui.size()

#################################################### LOOP START ########################################################
while True:
    ###################################### DETECTING HAND LANDMARKS ###############################################
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)

    ############################# RECORDING TIP OF INDEX AND MIDDLE FINGERS #######################################
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]


    ################################## CHECKING THE STATE OF FINGERS ##############################################

    fingers = detector.fingersUp()

    cv2.rectangle(img, (frameR, frameR), (widthCam - frameR, heightCam - frameR),
                  (255, 0, 0), 2)
    ########################### CURSOR WILL MOVE WHEN ONLY INDEX FINGER IS UP #####################################

    if fingers[1] == 1 and fingers[2] == 0:
        ######################################## CONVERTING COORDINATES ###########################################

        x3 = np.interp(x1, (frameR, widthCam - frameR), (0, widthScr))
        y3 = np.interp(y1, (frameR, heightCam - frameR), (0, heightScr))
        ############################################ SMOOTHENING VALUES ###########################################

        currentLocationX = pastLocationX + (x3 - pastLocationX) / smoothening
        currentLocationY = pastLocationY + (y3 - pastLocationY) / smoothening

        ################################################ MOVING MOUSE #############################################

        pyautogui.moveTo(widthScr - currentLocationX, currentLocationY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        pastLocationX, pastLocationY = currentLocationX, currentLocationY

    ################################ CURSOR WILL ONLY CLICK WHEN BOTH FINGERS ARE UP ##############################

    if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:

        ####################### STORING DISTANCE BETWEEN THE INDEX FINGER AND MIDDLE FINGER ####################

        length, img, lineInfo = detector.findDistance(8, 12, img)
        print(length)

        ################################# CLICKING FUNCTION OF CURSOR #########################################

        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                       15, (0, 255, 0), cv2.FILLED)
            #autopy.mouse.click()
            pyautogui.click()

        ############################################ HOLD FUNCTION #############################################

    if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 1:



            ################################################ MOVING MOUSE #############################################
            length, img, lineInfo = detector.findDistance(4, 8, img)

            if length < 40:
                ######################################## CONVERTING COORDINATES ###########################################
                x3 = np.interp(x1, (frameR, widthCam - frameR), (0, widthScr))
                y3 = np.interp(y1, (frameR, heightCam - frameR), (0, heightScr))
                ############################################ SMOOTHENING VALUES ###########################################
                currentLocationX = pastLocationX + (x3 - pastLocationX) / smoothening
                currentLocationY = pastLocationY + (y3 - pastLocationY) / smoothening

                print("draging")
                cv2.circle(img, (lineInfo[4], lineInfo[5]),
                           15, (0, 0, 0), cv2.FILLED)

                pyautogui.mouseDown()
                pyautogui.moveTo(widthScr - currentLocationX, currentLocationY)
    if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
            print("releasing")
            pyautogui.mouseUp()


        ########################################### SCROLL FUNCTION ############################################

    if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
        pyautogui.scroll(500)
        print("scrollup")
    if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        pyautogui.scroll(-500)
        print("scrolldown")

    #################################################  FRAME RATE #################################################

    currentTime = time.time()
    fps = 1 / (currentTime - pastTime)
    pastTime = currentTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (0, 0, 255), 3)

    ######################################  DISPLAY AND EXIT USING 'q' INPUT #######################################

    #cv2.imshow("GRV's PLAYGROUND", img)

    if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 1 and fingers[4] == 1:
        response = pyautogui.confirm(text='exit', title='grv', buttons=['Yes', 'No'])
        if response == "Yes":
            break
