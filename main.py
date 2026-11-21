
import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math
import urllib.request
from pathlib import Path

# ---------------- CONFIGURATION ----------------
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
SMOOTHING = 0.25
PINCH_THRESHOLD = 0.055
RELEASE_THRESHOLD = 0.085
CLICK_COOLDOWN = 0.45
SCROLL_SENSITIVITY = 0.015

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/"
    "hand_landmarker.task"
)

MODEL_PATH = Path(__file__).parent / "hand_landmarker.task"

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

screen_w, screen_h = pyautogui.size()

# ---------------- MODEL SETUP ----------------
if not MODEL_PATH.exists():
    print("Downloading MediaPipe hand model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Model downloaded successfully!")

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
RunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=str(MODEL_PATH)
    ),
    running_mode=RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.5,
)

# ---------------- HELPER FUNCTIONS ----------------
def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def finger_up(points, tip, pip):
    wrist = points[0]
    return distance(points[tip], wrist) > (
        distance(points[pip], wrist) * 1.12
    )


def draw_hand(frame, points):
    h, w = frame.shape[:2]

    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (5, 9), (9, 10), (10, 11), (11, 12),
        (9, 13), (13, 14), (14, 15), (15, 16),
        (13, 17), (17, 18), (18, 19), (19, 20),
        (0, 17),
    ]

    for a, b in connections:
        x1 = int(points[a].x * w)
        y1 = int(points[a].y * h)
        x2 = int(points[b].x * w)
        y2 = int(points[b].y * h)
        cv2.line(frame, (x1, y1), (x2, y2),
                 (0, 220, 180), 2)

    for point in points:
        x = int(point.x * w)
        y = int(point.y * h)
        cv2.circle(frame, (x, y), 4,
                   (255, 255, 255), -1)


# ---------------- CAMERA SETUP ----------------
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

if not cap.isOpened():
    raise RuntimeError(
        "Camera unavailable. Check camera permissions "
        "or change CAMERA_INDEX."
    )

prev_x, prev_y = pyautogui.position()
prev_scroll_y = None
last_click = 0
left_pinched = False
right_pinched = False
last_timestamp = -1
start_time = time.monotonic()

print("AI Virtual Mouse started!")
print("Press Q in the camera window to quit.")

prev_left_pinched = False
prev_right_pinched = False

try:
    with HandLandmarker.create_from_options(options) as detector:
        while True:
            success, frame = cap.read()
            if not success:
                print("Unable to read camera frame.")
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = np.ascontiguousarray(rgb)

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            timestamp = int(
                (time.monotonic() - start_time) * 1000
            )
            timestamp = max(timestamp, last_timestamp + 1)
            last_timestamp = timestamp

            result = detector.detect_for_video(
                mp_image, timestamp
            )

            status = "NO HAND"

            if result.hand_landmarks:
                points = result.hand_landmarks[0]
                draw_hand(frame, points)

                thumb = points[4]
                index = points[8]
                middle = points[12]

                index_up = finger_up(points, 8, 6)
                middle_up = finger_up(points, 12, 10)

                left_dist = distance(thumb, index)
                right_dist = distance(thumb, middle)

                # Hysteresis prevents rapid click flickering
                if left_pinched:
                    left_pinched = (
                        left_dist < RELEASE_THRESHOLD
                    )
                else:
                    left_pinched = (
                        left_dist < PINCH_THRESHOLD
                    )

                if right_pinched:
                    right_pinched = (
                        right_dist < RELEASE_THRESHOLD
                    )
                else:
                    right_pinched = (
                        right_dist < PINCH_THRESHOLD
                    )

                now = time.monotonic()

                
                # Priority 1: Left click
                if left_pinched and not right_pinched:
                    status = "LEFT PINCH"

                    if not prev_left_pinched and now - last_click > CLICK_COOLDOWN:
                        pyautogui.click(button="left")
                        last_click = now

                    prev_scroll_y = None

                # Priority 2: Right click
                elif right_pinched and not left_pinched:
                    status = "RIGHT PINCH"

                    if not prev_right_pinched and now - last_click > CLICK_COOLDOWN:
                        pyautogui.click(button="right")
                        last_click = now

                    prev_scroll_y = None


                
                # Priority 3: Scroll
                elif index_up and middle_up:
                    status = "SCROLL"

                    current_y = (points[8].y + points[12].y) / 2

                    if prev_scroll_y is not None:
                        delta = prev_scroll_y - current_y

                        if abs(delta) >= SCROLL_SENSITIVITY:
                            steps = max(1, min(4, int(abs(delta) / SCROLL_SENSITIVITY)))
                            direction = 1 if delta > 0 else -1

                            pyautogui.scroll(direction * steps)
                            prev_scroll_y = current_y
                    else:
                        prev_scroll_y = current_y


                # Priority 4: Move cursor
                elif index_up and not middle_up:
                    status = "MOVE"
                    prev_scroll_y = None

                    target_x = np.interp(
                        index.x, [0.12, 0.88],
                        [5, screen_w - 6]
                    )
                    target_y = np.interp(
                        index.y, [0.12, 0.88],
                        [5, screen_h - 6]
                    )

                    target_x = np.clip(
                        target_x, 5, screen_w - 6
                    )
                    target_y = np.clip(
                        target_y, 5, screen_h - 6
                    )

                    prev_x += (
                        target_x - prev_x
                    ) * SMOOTHING
                    prev_y += (
                        target_y - prev_y
                    ) * SMOOTHING

                    pyautogui.moveTo(
                        int(prev_x), int(prev_y),
                        duration=0
                    )

                else:
                    status = "IDLE"
                    prev_scroll_y = None
                prev_left_pinched = left_pinched
                prev_right_pinched = right_pinched
            else:
                left_pinched = False
                right_pinched = False
                prev_scroll_y = None

            # ---------------- INTERFACE ----------------
            cv2.rectangle(
                frame, (0, 0), (w, 70),
                (25, 25, 35), -1
            )

            cv2.putText(
                frame, "AI VIRTUAL MOUSE",
                (18, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (255, 255, 255), 2
            )

            cv2.putText(
                frame, f"Mode: {status}",
                (18, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (0, 255, 180), 2
            )

            cv2.putText(
                frame, "Press Q to quit",
                (15, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 1
            )

            cv2.imshow("AI Virtual Mouse", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

except pyautogui.FailSafeException:
    print("Emergency stop: mouse reached failsafe corner.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("AI Virtual Mouse stopped.")
