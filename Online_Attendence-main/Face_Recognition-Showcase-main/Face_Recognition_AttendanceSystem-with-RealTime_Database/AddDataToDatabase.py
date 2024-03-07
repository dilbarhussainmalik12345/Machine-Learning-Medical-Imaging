import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://fcaeattendancerealtime-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

data = {
    "321654":
        {
            "name":"Mohammad Yaqoob",
            "major":"Computer Science",
            "starting_year":2021,
            "total_attendance":6,
            "standing":"G",
            "year":3,
            "last_attendance_time":"2022-12-11 00:54:34"
        },
"852741":
        {
            "name":"Dilbar Hussain",
            "major":"Computer Science",
            "starting_year":2020,
            "total_attendance":12,
            "standing":"B",
            "year":4,
            "last_attendance_time":"2022-12-11 00:54:34"
        },
"963852":
        {
            "name":"Elon Musk",
            "major":"Robotics",
            "starting_year":2018,
            "total_attendance":7,
            "standing":"G",
            "year":4,
            "last_attendance_time":"2022-12-11 00:54:34"
        }
}

for key,value in data.items():
    ref.child(key).set(value)
