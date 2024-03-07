import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://fcaeattendancerealtime-default-rtdb.firebaseio.com/",
    'storageBucket':"fcaeattendancerealtime.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.png")

foldermodepath = 'Resources/Modes'
modepathlist = os.listdir(foldermodepath)

imgmodelist = []
for filename in modepathlist:
    filepath = os.path.join(foldermodepath, filename)
    imgmodelist.append(cv2.imread(filepath))
#print(len(imgmodelist))

# Load the Encoding Files
print("Loading Started.......")
file = open("EncodeFile.p",'rb')
encodeLIstKnownWithIds = pickle.load(file)
file.close()
encodeLIstKnown,studentIds = encodeLIstKnownWithIds
# print(studentIds)

print("Loading Compelete")


modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture a frame.")
        break

    img = cv2.resize(img, (640, 480))

    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgmodelist[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches = face_recognition.compare_faces(encodeLIstKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeLIstKnown,encodeFace)
            # print("Matches",matches)
            # print("Face_Distance",faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Matches_Index",matchIndex)

            if matches[matchIndex]:
                # print("Know Face Detected")
                # print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)

                    counter = 1
                    modeType = 1

        if counter!=0:

            if counter==1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # getting the data
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                # updating the data

                datetimeobject = datetime.strptime(studentInfo['last_attendance_time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeobject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed>30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgmodelist[modeType]

            if modeType!= 3:

                if 10<counter<20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgmodelist[modeType]

                if counter<=10:


                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),
                                cv2.FONT_HERSHEY_COMPLEX ,1,(255,255,255),1)

                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)



                    (w, h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1 ,1)
                    offest = (414-w)//2

                    cv2.putText(imgBackground, str(studentInfo['name']), (808+offest, 445),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[175:175+216,909:909+216] = imgStudent

                counter+=1

                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []

                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgmodelist[modeType]
    else:
        modeType = 0
        counter = 0
    #cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance",imgBackground)
    cv2.waitKey(1)


