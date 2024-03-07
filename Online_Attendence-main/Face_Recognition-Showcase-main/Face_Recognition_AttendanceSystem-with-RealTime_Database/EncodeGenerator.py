import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://fcaeattendancerealtime-default-rtdb.firebaseio.com/",
    'storageBucket':"fcaeattendancerealtime.appspot.com"
})



folderpath = 'Images'
pathlist = os.listdir(folderpath)
print(pathlist)

imglist = []
studentIds = []
for path in pathlist:
    filepath = os.path.join(folderpath, path)
    imglist.append(cv2.imread(filepath))
    studentIds.append(os.path.splitext(path)[0])

    # Uploding Images to Bucket

    fileName = f'{folderpath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


    # print(path)
    # print(os.path.splitext(path)[0])

print(studentIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(img)
        encode = face_recognition.face_encodings(img,face_locations)[0]
        encodeList.append(encode)
    return encodeList

print("Encode Started.......")
encodeLIstKnown = findEncodings(imglist)
encodeLIstKnownWithIds = [encodeLIstKnown,studentIds]
print(encodeLIstKnown)
print("Encode Complete")

file = open("EncodeFile.p",'wb')
pickle.dump(encodeLIstKnownWithIds,file)
file.close()
print("File  Saved")


