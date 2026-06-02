# CS131-EDGE-Project







## References for face detection and video streaming:

MediaPipe guides and model:
https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/face_landmarker/python/%5BMediaPipe_Python_Tasks%5D_Face_Landmarker.ipynb
https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/python#live-stream_1
https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker/index#models

https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html

https://github.com/google-ai-edge/mediapipe-samples/tree/main/examples/face_landmarker/raspberry_pi

## MQTT Instructions (Linux):
### Both devices
  - Create VENV: python3 -m venv env
  - Activate VENV: source env/bin/activate
  - Install paho-mqtt: pip install paho-mqtt

### Edge Device 1 (Subscriber/Broker/Vision)
- Add Firebase credentials JSON key to project folder
- Update credentials path in TestVision.py
- Install Dependencies (inside activated venv)
  - pip install firebase-admin
  - pip install playsound
- Install Mosquitto
  - sudo apt update && sudo apt install mosquitto mosquitto-clients
- Run Mosquitto with config file
  - sudo cp mosquitto.conf /etc/mosquitto/mosquitto.conf
  - sudo systemctl restart mosquitto
  - sudo systemctl enable mosquitto
  - sudo systemctl status mosquitto
- Get IP and update "BrokerIP" in both TestVision.py and accelerometer.py
  - hostname -I
- Run computer vision: python3 TestVision.py

### Edge Device 2 (Publisher/Accelerometer)
- Install Dependencies (inside activated venv)
  - pip install smbus2
- Run accelerometer: python3 accelerometer.py

### Mosquitto cmds:
- Display connection and port status: netstat -an | grep 1883
- View broker logs: sudo journalctl -u mosquitto -f


