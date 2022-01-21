from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate
from PyQt5.QtWidgets import QDialog, QMessageBox
import cv2
import face_recognition as fr
import numpy as np
import datetime
import os

path = "Images"      #path where pictures are store

class Ui_OutputWindow(QDialog):
    def __init__(self):
        super(Ui_OutputWindow, self).__init__()
        loadUi("./outputwindow.ui", self)
        
        self.logic = 0
        self.value = 0
        self.start = 0
        self.end = 0
        self.name = ""
        self.ClockIn = False
        #self.ClockOut = False
        self.image = None
        
        self.startHour = self.endHour = 0
        self.startMin = self.endMin = 0
        self.startSec = self.endSec = 0
        
        self.SCREENSHOT.clicked.connect(self.onClickSS)        
        self.TEXT.setText("WELCOME!!")
        
        #Update time
        now = QDate.currentDate()
        current_date = now.toString(' ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime(" %I:%M %p")
        self.DATE.setText(current_date)
        self.TIME.setText(current_time)
        
        self.CLOCK_IN.clicked.connect(self.In)
        self.CLOCK_OUT.clicked.connect(self.Out)
        
                
    @pyqtSlot()       
    def markAttendance(self, name):
        
        if self.ClockIn == True:
            with open("Attendance.csv", "r+") as f:
                myData = f.readlines()
                nameList = []
                for line in myData:
                    entry = line.split(",")
                    nameList.append(entry[0])
                if name not in nameList:
                    now = datetime.datetime.now()
                    dtString = now.strftime("%H:%M:%S")
                    f.writelines(f"\n{name}, {dtString}")
                
                
    def startVideo(self):
        self.TEXT.setText("Clock In to Capture an Image!!")
        
        self.capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.timer = QTimer(self)  # Create Timer
        
        #Storing Names of the Students from the Picture Caption
        images = []          #store images
        self.students = []        #store names of the students
        self.encodeList = []    #store the encodings for the images

        myList = os.listdir(path)      #have names like Esha.jpg, Vivek,jpg

        for name in myList:
            curImg = cv2.imread(f"{path}/{name}")           #read images from the folder
            images.append(curImg)
            self.students.append(os.path.splitext(name)[0])      #store names as Esha, Vivek
                                             
        #Finding encodings for the image
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = fr.face_encodings(img)[0]
            self.encodeList.append(encode)
              
        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(10)
 
        
    def update_frame(self):
        success, self.image = self.capture.read()
        self.displayImage(self.image, self.encodeList, self.students, 1)
        
        if success == True:
            
            if self.ClockIn == True and self.logic == 2:
                    
                buttonReply = QMessageBox.question(self, 'Screenshot', 'Save or not?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                self.logic = 1
                
                if buttonReply == QMessageBox.Yes:
                    self.value = self.value + 1
                    cv2.imwrite("C:\Face_Recognition\Screenshot\%s.jpg"%(self.value), self.image)
                                            
                    self.TEXT.setText("Your Image Saved!!\nFor another Screenshot press \"SCREENSHOT\" again.")
                else:
                    self.TEXT.setText("Screenshot not Captured!")
            else:
                self.logic = 1
                
        
    def face_rec_(self, image, encodeList, students):
        
       #face recognition
       faces_cur_frame = fr.face_locations(image)
       encodes_cur_frame = fr.face_encodings(image, faces_cur_frame)
              
       for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
           match = fr.compare_faces(encodeList, encodeFace, tolerance = 0.50)
           face_dis = fr.face_distance(encodeList, encodeFace)
           name = "UNKNOWN"
           best_match_index = np.argmin(face_dis)
          
           if match[best_match_index]:
               name = students[best_match_index].upper()
               self.NAME.setText(name)
               self.markAttendance(name)
           
           y1, x2, y2, x1 = faceLoc
           if name != "UNKNOWN":           
               cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
               cv2.rectangle(image, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)               
           else:
               cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
               cv2.rectangle(image, (x1, y2 - 20), (x2, y2), (0, 0, 255), cv2.FILLED)               
           cv2.putText(image, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        
       return image
       
        
    def displayImage(self, image, encodeList, students, window = 1):
        
        imgS = cv2.resize(image, (640, 480))
        self.face_rec_(image, encodeList, students)
        
        qformat = QImage.Format_Indexed8
        if len(imgS.shape) == 3:
            if imgS.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        if window == 1:
            self.WebCam.setPixmap(QPixmap.fromImage(outImage))
            self.WebCam.setScaledContents(True)
        
                                     
    def In(self):
        
        buttonReply = QMessageBox.question(self, 'Welcome', 'Are you Clocking In?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if buttonReply == QMessageBox.Yes:  
            self.ClockIn = True
            self.TEXT.setText("Kindly Press \"SCREENSHOT\" to Capture an Image!!")
            self.STATUS.setText(" Clocked In")
            self.start = datetime.datetime.now().strftime(" %I:%M:%S")
            self.startHour = int(self.start[1:3])
            self.startMin = int(self.start[4:6])
            self.startSec = int(self.start[7:])
            
            self.HOUR.setText(" Calculating!!....")
            self.MIN.setText(" ")
            self.SEC.setText(" ")           
            
        else:
            self.ClockIn = False
    
    
    def Out(self):
        buttonReply = QMessageBox.question(self, 'Class Over', 'Are you Clocking Out?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if buttonReply == QMessageBox.Yes:  
            self.STATUS.setText(" Clocked Out")
            
            #self.ClockOut = True
            self.end = datetime.datetime.now().strftime(" %I:%M:%S")
            self.endHour = int(self.end[1:3])
            self.endMin = int(self.end[4:6])
            self.endSec = int(self.end[7:])
            self.HOUR.setText(f" {abs(self.endHour - self.startHour)}h")
            self.MIN.setText(f" {abs(self.endMin - self.startMin)}m")
            self.SEC.setText(f" {abs(self.endSec - self.startSec)}s")
            
            self.WebCam.setText("CLASS OVER!!")
            self.TEXT.setText("Class Over! No Screenshot will be captured now.")
            #self.NAME.setText("Attandance Marked!")
            
            self.capture.release()
            cv2.destroyAllWindows()
    
    
    def onClickSS(self):
        self.logic = 2