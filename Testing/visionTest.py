import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, firestore
import random
import datetime
import time

cred = credentials.Certificate("/pathtokey/.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

BrokerIP = "IP HERE"

state = {"accel_alert": False, "vision_alert": False} 
last_alert_time = 0
alert_start_time = None

def trigger_alert(duration):
    print(f"Both eyes closed and erratic driving detected for: {round(duration,2)}s.")
    
def send_alert_msg(duration):    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.collection("alerts").add({"message": "Unsafe Driving Detected", "time": current_time, "duration": round(duration, 2)})
    print("Alert sent to cloud.")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"On Message Fires - Topic: {msg.topic}, Payload: {payload}")
    
    if msg.topic == "driver/accel":
        state["accel_alert"] = payload == "ALERT"
        print(f"Received accel state: {payload}")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to broker: {reason_code}")
    client.subscribe("driver/accel") 

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect 
client.on_message = on_message
client.connect(BrokerIP, 1883)
client.loop_start()

def main():
    global alert_start_time, last_alert_time

    print("Vision simulating...")

    while True:
        blink_score = random.uniform(0.3, 1)
        alert = blink_score > 0.5
        state["vision_alert"] = alert

        payload = "ALERT" if alert else "CLEAR"
        client.publish("driver/vision", payload)
        print(f"Eye Score: {blink_score:.2f} - published: {payload}")

        if state["accel_alert"] and state["vision_alert"]:
            now = time.time()

            if alert_start_time is None:
                alert_start_time = now

            duration = now - alert_start_time
            trigger_alert(duration)

            last_cloud_msg = now - last_alert_time

            if last_cloud_msg >= 10 and duration >= 3:
                last_alert_time = now
                send_alert_msg(duration)
                print("Log sent successfully.")
        else:
            alert_start_time = None

        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Stopping...")
        client.disconnect()