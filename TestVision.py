import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
import cv2
import numpy as np

model_path = r'C:\Users\Vitik\Documents\GitHub\CS131-EDGE-Project\face_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

annotated_frame = None

def process_result(result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global annotated_frame
    
    annotated_image = np.copy(output_image.numpy_view())
    

    if result.face_blendshapes:
        for face_blendshapes in result.face_blendshapes:
            for item in face_blendshapes:
                if item.category_name == 'eyeBlinkLeft':
                    left_blink_score = item.score
                elif item.category_name == 'eyeBlinkRight':
                    right_blink_score = item.score
        
            left_eye_closed = left_blink_score > 0.5
            right_eye_closed = right_blink_score > 0.5
            
            print(f"Left Eye Closed: {left_eye_closed} ({left_blink_score:.2f}), Right Eye Closed: {right_eye_closed} ({right_blink_score:.2f})")
    

    for face_landmarks in result.face_landmarks:

        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks,
            connections=vision.FaceLandmarksConnections.FACE_LANDMARKS_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_tesselation_style())
        
        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks,
            connections=vision.FaceLandmarksConnections.FACE_LANDMARKS_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_contours_style())
        
        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks,
            connections=vision.FaceLandmarksConnections.FACE_LANDMARKS_LEFT_IRIS,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_iris_connections_style())
        
        drawing_utils.draw_landmarks(
            image=annotated_image,
            landmark_list=face_landmarks,
            connections=vision.FaceLandmarksConnections.FACE_LANDMARKS_RIGHT_IRIS,
            landmark_drawing_spec=None,
            connection_drawing_spec=drawing_styles.get_default_face_mesh_iris_connections_style())

    annotated_frame = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    output_face_blendshapes=True, 
    result_callback=process_result)

vidLive = cv2.VideoCapture(0)

with FaceLandmarker.create_from_options(options) as landmarker:
    if not vidLive.isOpened():
        print("Error: Could not open webcam.")
        exit()
    
    while True:
        ret, frame = vidLive.read()
        msTime = int(time.time() * 1000)
        
        if not ret:
            print("Error: Can't receive frame. Exiting...")
            break

        rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgbFrame)
        
        landmarker.detect_async(mp_image, msTime)
        

        if annotated_frame is not None:
            cv2.imshow('Face Landmarker', annotated_frame)
        else:
            cv2.imshow('Face Landmarker', frame)

        if cv2.waitKey(1) == ord('q'):
            break


    vidLive.release()
    cv2.destroyAllWindows()