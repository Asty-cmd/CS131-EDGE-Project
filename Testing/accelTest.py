import paho.mqtt.client as mqtt
import time
import random

BrokerIP = "IP HERE"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BrokerIP, 1883)
client.loop_start()

print("Accelerometer simulating..")

while True:
    accel_value = random.uniform(2.2,4)
    alert = accel_value > 2.5

    payload = "ALERT" if alert else "CLEAR"
    client.publish("driver/accel", payload)
    print(f"Accel Value: {accel_value:.2f}g - published: {payload}")

    time.sleep(1)

