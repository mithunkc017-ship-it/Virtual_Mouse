import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import math
import urllib.request
import os
from pathlib import Path
from datetime import datetime

# ============================================================
# AI VIRTUAL MOUSE 2.0 - HANDS-FREE WINDOWS DESKTOP CONTROLLER
# Existing controls are preserved and extended.
# ============================================================

# ---------------- CONFIGURATION ----------------
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Cursor movement
BASE_SMOOTHING = 0.25
MIN_SMOOTHING = 0.25
MAX_SMOOTHING = 0.75
MOUSE_MARGIN = 6

# Pinch detection (normalized landmark distance)
PINCH_THRESHOLD = 0.055
RELEASE_THRESHOLD = 0.085
CLICK_COOLDOWN = 0.45

# Scroll
SCROLL_SENSITIVITY = 0.015
MAX_SCROLL_STEPS = 5

# Gesture safety
GESTURE_HOLD_SECONDS = 0.65
ACTION_COOLDOWN = 1.2
VOLUME_STEP_COOLDOWN = 0.16
VOLUME_MOVEMENT_THRESHOLD = 0.025

# Copilot Windows URI. Requires the Copilot desktop app to be installed
# and its URI protocol to be registered by Windows.
COPILOT_URI = "ms-copilot:"

# Files
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/"
    "hand_landmarker.task"
)
BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "hand_landmarker.task"
SCREENSHOT_DIR = BASE_DIR / "Screenshots"

# PyAutoGUI safety/performance
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
    base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
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
    """Retains the original wrist-distance finger test."""
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
        x1, y1 = int(points[a].x * w), int(points[a].y * h)
        x2, y2 = int(points[b].x * w), int(points[b].y * h)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 220, 180), 2)

    for point in points:
        x, y = int(point.x * w), int(point.y * h)
        cv2.circle(frame, (x, y), 4, (255, 255, 255), -1)


def move_cursor(index_point, previous_x, previous_y):
    """Adaptive smoothing: slower near the target, faster for large moves."""
    target_x = np.interp(
        index_point.x, [0.12, 0.88],
        [MOUSE_MARGIN, screen_w - MOUSE_MARGIN]
    )
    target_y = np.interp(
        index_point.y, [0.12, 0.88],
        [MOUSE_MARGIN, screen_h - MOUSE_MARGIN]
    )

    target_x = float(np.clip(target_x, MOUSE_MARGIN, screen_w - MOUSE_MARGIN))
    target_y = float(np.clip(target_y, MOUSE_MARGIN, screen_h - MOUSE_MARGIN))

    movement = math.hypot(target_x - previous_x, target_y - previous_y)
    alpha = min(MAX_SMOOTHING, max(
        MIN_SMOOTHING, BASE_SMOOTHING + movement / 700
    ))

    new_x = previous_x + (target_x - previous_x) * alpha
    new_y = previous_y + (target_y - previous_y) * alpha

    pyautogui.moveTo(int(new_x), int(new_y), duration=0)
    return new_x, new_y


def launch_copilot():
    """Open the installed Copilot app through its Windows URI."""
    try:
        os.startfile(COPILOT_URI)
        print("Opening Microsoft Copilot...")
        return "COPILOT"
    except OSError as exc:
        print(
            "Could not open Copilot desktop app. "
            "Check that it is installed and supports the URI "
            f"{COPILOT_URI!r}. Details: {exc}"
        )
        return "COPILOT NOT FOUND"


def take_screenshot():
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = SCREENSHOT_DIR / filename
    pyautogui.screenshot().save(path)
    print(f"Screenshot saved: {path}")
    return path


def draw_hud(frame, status, fps, gesture_hint):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 94), (25, 25, 35), -1)

    cv2.putText(
        frame, "AI VIRTUAL MOUSE 2.0",
        (16, 27), cv2.FONT_HERSHEY_SIMPLEX,
        0.68, (255, 255, 255), 2
    )
    cv2.putText(
        frame, f"Mode: {status}",
        (16, 55), cv2.FONT_HERSHEY_SIMPLEX,
        0.52, (0, 255, 180), 2
    )
    cv2.putText(
        frame, f"FPS: {fps:.1f}",
        (w - 115, 27), cv2.FONT_HERSHEY_SIMPLEX,
        0.52, (255, 255, 255), 1
    )
    cv2.putText(
        frame, gesture_hint,
        (16, 81), cv2.FONT_HERSHEY_SIMPLEX,
        0.40, (210, 210, 210), 1
    )
    cv2.putText(
        frame, "Press Q to quit | Move mouse to top-left for emergency stop",
        (12, h - 12), cv2.FONT_HERSHEY_SIMPLEX,
        0.38, (255, 255, 255), 1
    )


# ---------------- CAMERA SETUP ----------------
cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
# Reduce camera buffering on backends that support it.
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    raise RuntimeError(
        "Camera unavailable. Check camera permissions "
        "or change CAMERA_INDEX."
    )

prev_x, prev_y = pyautogui.position()
prev_scroll_y = None
prev_volume_y = None

left_pinched = False
right_pinched = False
left_mouse_is_down = False
previous_right_pinched = False

last_timestamp = -1
start_time = time.monotonic()
last_frame_time = start_time
fps = 0.0

# Per-action cooldowns and hold timers
last_action_time = {}
gesture_start_time = {}
gesture_fired = set()
last_volume_action = 0.0
last_click = 0.0

def action_ready(name, cooldown=ACTION_COOLDOWN):
    now = time.monotonic()
    if now - last_action_time.get(name, 0.0) >= cooldown:
        last_action_time[name] = now
        return True
    return False


def held_long_enough(name, active):
    """Return True once a gesture has been held for the configured time."""
    now = time.monotonic()
    if not active:
        gesture_start_time.pop(name, None)
        gesture_fired.discard(name)
        return False

    if name in gesture_fired:
        return False

    if name not in gesture_start_time:
        gesture_start_time[name] = now
        return False

    if now - gesture_start_time[name] >= GESTURE_HOLD_SECONDS:
        gesture_fired.add(name)
        return True

    return False


print("AI Virtual Mouse 2.0 started!")
print("Press Q in the camera window to quit.")
print("Keep your hand clearly visible and use one gesture at a time.")

try:
    with HandLandmarker.create_from_options(options) as detector:
        while True:
            success, frame = cap.read()
            if not success:
                print("Unable to read camera frame.")
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            # OpenCV -> RGB -> MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = np.ascontiguousarray(rgb)
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            timestamp = int((time.monotonic() - start_time) * 1000)
            timestamp = max(timestamp, last_timestamp + 1)
            last_timestamp = timestamp

            result = detector.detect_for_video(mp_image, timestamp)
            status = "NO HAND"
            gesture_hint = "Show one hand to the camera"

            if result.hand_landmarks:
                points = result.hand_landmarks[0]
                draw_hand(frame, points)

                thumb = points[4]
                index = points[8]
                middle = points[12]
                ring = points[16]
                pinky = points[20]

                index_up = finger_up(points, 8, 6)
                middle_up = finger_up(points, 12, 10)
                ring_up = finger_up(points, 16, 14)
                pinky_up = finger_up(points, 20, 18)

                # Thumb-up uses vertical thumb extension and curled fingers.
                thumb_up = (
                    points[4].y < points[3].y
                    and not index_up
                    and not middle_up
                    and not ring_up
                    and not pinky_up
                )

                left_dist = distance(thumb, index)
                right_dist = distance(thumb, middle)

                # Hysteresis avoids pinch flicker.
                if left_pinched:
                    left_pinched = left_dist < RELEASE_THRESHOLD
                else:
                    left_pinched = left_dist < PINCH_THRESHOLD

                if right_pinched:
                    right_pinched = right_dist < RELEASE_THRESHOLD
                else:
                    right_pinched = right_dist < PINCH_THRESHOLD

                now = time.monotonic()

                # ------------------------------------------------
                # 1. LEFT PINCH: click on release / drag while held
                # ------------------------------------------------
                if left_pinched and not right_pinched:
                    status = "DRAG / LEFT CLICK"
                    gesture_hint = "Pinch thumb + index; move to drag; release to drop"

                    # Move while pinched so the held mouse button can drag.
                    prev_x, prev_y = move_cursor(index, prev_x, prev_y)

                    if not left_mouse_is_down:
                        pyautogui.mouseDown(button="left")
                        left_mouse_is_down = True

                    prev_scroll_y = None
                    prev_volume_y = None

                else:
                    # Releasing the pinch completes a normal click or drag.
                    if left_mouse_is_down:
                        pyautogui.mouseUp(button="left")
                        left_mouse_is_down = False

                    # --------------------------------------------
                    # 2. RIGHT PINCH: right click on pinch start
                    # --------------------------------------------
                    if right_pinched:
                        status = "RIGHT CLICK"
                        gesture_hint = "Pinch thumb + middle finger"

                        # Rising-edge detection is handled below using
                        # previous_right_pinched.
                        if not previous_right_pinched and now - last_click > CLICK_COOLDOWN:
                            pyautogui.click(button="right")
                            last_click = now

                        prev_scroll_y = None
                        prev_volume_y = None

                    # --------------------------------------------
                    # 3. TWO FINGERS: scroll (existing control)
                    # --------------------------------------------
                    elif index_up and middle_up and not ring_up and not pinky_up:
                        status = "SCROLL"
                        gesture_hint = "Index + middle fingers; move hand up/down"

                        current_y = (points[8].y + points[12].y) / 2

                        if prev_scroll_y is not None:
                            delta = prev_scroll_y - current_y
                            if abs(delta) >= SCROLL_SENSITIVITY:
                                steps = max(
                                    1,
                                    min(
                                        MAX_SCROLL_STEPS,
                                        int(abs(delta) / SCROLL_SENSITIVITY)
                                    )
                                )
                                direction = 1 if delta > 0 else -1
                                pyautogui.scroll(direction * steps)
                                prev_scroll_y = current_y
                        else:
                            prev_scroll_y = current_y

                        prev_volume_y = None

                    # --------------------------------------------
                    # 4. FOUR FINGERS OPEN: volume by hand movement
                    # --------------------------------------------
                    elif index_up and middle_up and ring_up and pinky_up:
                        status = "VOLUME CONTROL"
                        gesture_hint = "Open palm: move up = volume up; down = volume down"

                        palm_y = points[9].y
                        if prev_volume_y is not None:
                            delta = prev_volume_y - palm_y
                            if (
                                abs(delta) >= VOLUME_MOVEMENT_THRESHOLD
                                and now - last_volume_action >= VOLUME_STEP_COOLDOWN
                            ):
                                if delta > 0:
                                    pyautogui.press("volumeup")
                                    status = "VOLUME UP"
                                else:
                                    pyautogui.press("volumedown")
                                    status = "VOLUME DOWN"

                                last_volume_action = now
                                prev_volume_y = palm_y
                        else:
                            prev_volume_y = palm_y

                        prev_scroll_y = None

                    # --------------------------------------------
                    # 5. THUMBS UP: launch Copilot after hold
                    # --------------------------------------------
                    elif thumb_up:
                        status = "COPILOT GESTURE"
                        gesture_hint = "Hold thumbs up to open Copilot"

                        if (
                            held_long_enough("copilot", True)
                            and action_ready("copilot")
                        ):
                            status = launch_copilot()

                        prev_scroll_y = None
                        prev_volume_y = None

                    # --------------------------------------------
                    # 6. RING ONLY: double click after hold
                    # --------------------------------------------
                    elif ring_up and not index_up and not middle_up and not pinky_up:
                        status = "DOUBLE CLICK GESTURE"
                        gesture_hint = "Hold ring finger up to double-click"

                        if (
                            held_long_enough("double_click", True)
                            and action_ready("double_click")
                        ):
                            pyautogui.doubleClick(interval=0.12)
                            status = "DOUBLE CLICK"

                        prev_scroll_y = None
                        prev_volume_y = None

                    # --------------------------------------------
                    # 7. PINKY ONLY: screenshot after hold
                    # --------------------------------------------
                    elif pinky_up and not index_up and not middle_up and not ring_up:
                        status = "SCREENSHOT GESTURE"
                        gesture_hint = "Hold little finger up to take screenshot"

                        if (
                            held_long_enough("screenshot", True)
                            and action_ready("screenshot")
                        ):
                            take_screenshot()
                            status = "SCREENSHOT SAVED"

                        prev_scroll_y = None
                        prev_volume_y = None

                    # --------------------------------------------
                    # 8. INDEX + MIDDLE + RING: Alt + Tab
                    # --------------------------------------------
                    elif index_up and middle_up and ring_up and not pinky_up:
                        status = "WINDOW SWITCH GESTURE"
                        gesture_hint = "Hold index + middle + ring to switch window"

                        if (
                            held_long_enough("alt_tab", True)
                            and action_ready("alt_tab")
                        ):
                            pyautogui.hotkey("alt", "tab")
                            status = "ALT + TAB"

                        prev_scroll_y = None
                        prev_volume_y = None

                    # --------------------------------------------
                    # 9. INDEX + PINKY: media play/pause
                    # --------------------------------------------
                    elif index_up and pinky_up and not middle_up and not ring_up:
                        status = "MEDIA GESTURE"
                        gesture_hint = "Hold index + little finger for play/pause"

                        if (
                            held_long_enough("play_pause", True)
                            and action_ready("play_pause")
                        ):
                            pyautogui.press("playpause")
                            status = "PLAY / PAUSE"

                        prev_scroll_y = None
                        prev_volume_y = None

                    # --------------------------------------------
                    # 10. INDEX ONLY: move cursor (existing control)
                    # --------------------------------------------
                    elif index_up and not middle_up and not ring_up and not pinky_up:
                        status = "MOVE"
                        gesture_hint = "Index finger: move cursor"

                        prev_x, prev_y = move_cursor(index, prev_x, prev_y)
                        prev_scroll_y = None
                        prev_volume_y = None

                    else:
                        status = "IDLE"
                        gesture_hint = "Use a gesture shown in the controls"
                        prev_scroll_y = None
                        prev_volume_y = None

                # Update pinch edge state.
                previous_right_pinched = right_pinched

                # Reset hold timers when their gesture is no longer active.
                active_holds = {
                    "copilot": thumb_up,
                    "double_click": (
                        ring_up and not index_up and not middle_up and not pinky_up
                    ),
                    "screenshot": (
                        pinky_up and not index_up and not middle_up and not ring_up
                    ),
                    "alt_tab": (
                        index_up and middle_up and ring_up and not pinky_up
                    ),
                    "play_pause": (
                        index_up and pinky_up and not middle_up and not ring_up
                    ),
                }
                for hold_name, is_active in active_holds.items():
                    if not is_active:
                        gesture_start_time.pop(hold_name, None)
                        gesture_fired.discard(hold_name)

            else:
                # If tracking is lost during a drag, always release the mouse.
                if left_mouse_is_down:
                    pyautogui.mouseUp(button="left")
                    left_mouse_is_down = False

                left_pinched = False
                right_pinched = False
                previous_right_pinched = False
                prev_scroll_y = None
                prev_volume_y = None
                gesture_start_time.clear()
                gesture_fired.clear()
                status = "NO HAND"
                gesture_hint = "Show one hand to the camera"

            # FPS estimate
            frame_now = time.monotonic()
            frame_delta = frame_now - last_frame_time
            if frame_delta > 0:
                instant_fps = 1.0 / frame_delta
                fps = instant_fps if fps == 0 else (fps * 0.85 + instant_fps * 0.15)
            last_frame_time = frame_now

            draw_hud(frame, status, fps, gesture_hint)
            cv2.imshow("AI Virtual Mouse 2.0", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

except pyautogui.FailSafeException:
    print("Emergency stop: mouse reached the top-left failsafe corner.")

except KeyboardInterrupt:
    print("Stopped by keyboard interrupt.")

finally:
    # Never leave the left mouse button held after exiting.
    try:
        if left_mouse_is_down:
            pyautogui.mouseUp(button="left")
    except Exception:
        pass

    cap.release()
    cv2.destroyAllWindows()
    print("AI Virtual Mouse 2.0 stopped.")
