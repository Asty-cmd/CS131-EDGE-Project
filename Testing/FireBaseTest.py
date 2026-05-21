import firebase_admin
from firebase_admin import credentials, firestore
import datetime
cred = credentials.Certificate("/pathtokey/.json")
firebase_admin.initialize_app(cred)

current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
db = firestore.client()

db.collection("alerts").add({"message": "test", "time": current_time})
print("Log sent successfully.")