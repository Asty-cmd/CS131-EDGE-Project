import argparse
import sys
import time

import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Global variables to calculate FPS
COUNTER, FPS = 0, 0
START_TIME = time.time()
DETECTION_RESULT = None


def run(model: str, num_faces: int,
        min_face_detection_confidence: float,
        min_face_presence_confidence: float, min_tracking_confidence: float,
        camera_id: int, width: int, height: int) -> None:
    """Continuously run inference on images acquired from the camera."""

    cap = cv2.VideoCapture(camera_id)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    row_size = 50  
    left_margin = 24  
    text_color = (0, 0, 0)  
    font_size = 1
    font_thickness = 1
    fps_avg_frame_count = 10

    label_background_color = (255, 255, 255)  
    label_padding_width = 1500  

    def save_result(result: vision.FaceLandmarkerResult,
                    unused_output_image: mp.Image, timestamp_ms: int):
        global FPS, COUNTER, START_TIME, DETECTION_RESULT

        if COUNTER % fps_avg_frame_count == 0:
            FPS = fps_avg_frame_count / (time.time() - START_TIME)
            START_TIME = time.time()

        DETECTION_RESULT = result
        COUNTER += 1

    # Initialize the modern face landmarker model options
    base_options = python.BaseOptions(model_asset_path=model)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.LIVE_STREAM,
        num_faces=num_faces,
        min_face_detection_confidence=min_face_detection_confidence,
        min_face_presence_confidence=min_face_presence_confidence,
        min_tracking_confidence=min_tracking_confidence,
        output_face_blendshapes=True,
        result_callback=save_result)
    detector = vision.FaceLandmarker.create_from_options(options)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            sys.exit('ERROR: Unable to read from webcam.')

        image = cv2.flip(image, 1)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

        # Run face landmarker asynchronously
        detector.detect_async(mp_image, time.time_ns() // 1_000_000)

        fps_text = 'FPS = {:.1f}'.format(FPS)
        text_location = (left_margin, row_size)
        current_frame = image
        cv2.putText(current_frame, fps_text, text_location,
                    cv2.FONT_HERSHEY_DUPLEX,
                    font_size, text_color, font_thickness, cv2.LINE_AA)

        if DETECTION_RESULT:
            # Drawing landmarks using the new result structure, drawing manually 
            # to avoid relying on the deprecated mp.solutions.drawing_utils
            for face_landmarks in DETECTION_RESULT.face_landmarks:
                for landmark in face_landmarks:
                    x = int(landmark.x * current_frame.shape[1])
                    y = int(landmark.y * current_frame.shape[0])
                    cv2.circle(current_frame, (x, y), 1, (0, 255, 0), -1)

        # Expand the right side frame to show the blendshapes
        current_frame = cv2.copyMakeBorder(current_frame, 0, 0, 0,
                                           label_padding_width,
                                           cv2.BORDER_CONSTANT, None,
                                           label_background_color)

        if DETECTION_RESULT and DETECTION_RESULT.face_blendshapes:
          legend_x = current_frame.shape[1] - label_padding_width + 20  
          legend_y = 30  
          bar_max_width = label_padding_width - 40  
          bar_height = 8  
          gap_between_bars = 5  
          text_gap = 5  

          face_blendshapes = DETECTION_RESULT.face_blendshapes

          if face_blendshapes:
              for idx, category in enumerate(face_blendshapes[0]):
                  category_name = category.category_name
                  score = round(category.score, 2)

                  text = "{} ({:.2f})".format(category_name, score)
                  (text_width, _), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)

                  cv2.putText(current_frame, text,
                              (legend_x, legend_y + (bar_height // 2) + 5),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

                  bar_width = int(bar_max_width * score)
                  cv2.rectangle(current_frame,
                                (legend_x + text_width + text_gap, legend_y),
                                (legend_x + text_width + text_gap + bar_width, legend_y + bar_height),
                                (0, 255, 0), -1)

                  legend_y += (bar_height + gap_between_bars)

        cv2.imshow('face_landmarker', current_frame)

        if cv2.waitKey(1) == 27:
            break

    detector.close()
    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--model', help='Name of face landmarker model.', required=False, default='face_landmarker.task')
    parser.add_argument('--numFaces', help='Max number of faces to detect.', required=False, default=1)
    parser.add_argument('--minFaceDetectionConfidence', help='Min detection confidence.', required=False, default=0.5)
    parser.add_argument('--minFacePresenceConfidence', help='Min presence confidence.', required=False, default=0.5)
    parser.add_argument('--minTrackingConfidence', help='Min tracking confidence.', required=False, default=0.5)
    parser.add_argument('--cameraId', help='Id of camera.', required=False, default=0)
    parser.add_argument('--frameWidth', help='Width of frame.', required=False, default=1280)
    parser.add_argument('--frameHeight', help='Height of frame.', required=False, default=960)
    args = parser.parse_args()

    run(args.model, int(args.numFaces), args.minFaceDetectionConfidence,
        args.minFacePresenceConfidence, args.minTrackingConfidence,
        int(args.cameraId), args.frameWidth, args.frameHeight)


if __name__ == '__main__':
    main()