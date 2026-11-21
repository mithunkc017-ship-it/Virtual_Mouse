# AI Virtual Mouse 2.0

AI Virtual Mouse 2.0 is a hands-free Windows desktop controller that uses real-time hand gesture recognition through a webcam. It extends the original virtual mouse with drag-and-drop, volume control, screenshots, Copilot launching, window switching, media controls, and adaptive cursor movement.

The project uses MediaPipe Hand Landmarker for tracking, OpenCV for the camera preview and on-screen HUD, and PyAutoGUI for Windows mouse and keyboard automation.

The application is optimized for a webcam resolution of 640x480 and moves the cursor based on the position of the index finger.

## Features

- Real-time 21-point hand and finger tracking
- Adaptive, smoothed cursor movement
- Left-click and drag-and-drop gestures
- Right-click gesture
- Vertical scrolling
- Four-finger open-palm volume control
- Double-click gesture
- Screenshot capture
- Microsoft Copilot launcher
- Alt+Tab window switching
- Play/pause media control
- Hold timers and action cooldowns to prevent accidental repeated actions
- Hysteresis-based pinch detection
- Live FPS and gesture status HUD
- PyAutoGUI failsafe protection
- Webcam preview with hand landmarks and the current gesture mode
- Automatic MediaPipe model download on first launch
- Emergency stop by moving the mouse to the top-left screen corner
- Press `Q` to close the application

## Gesture Controls

| Gesture | Action |
|---|---|
| Raise only the index finger | Move the mouse cursor |
| Pinch the thumb and index finger | Hold and move to drag; release to click/drop |
| Pinch the thumb and middle finger | Right click |
| Raise the index and middle fingers | Scroll vertically |
| Open all four fingers | Move the hand up or down to adjust system volume |
| Hold thumbs up | Open Microsoft Copilot |
| Hold only the ring finger up | Double click |
| Hold only the little finger up | Take a screenshot |
| Hold index, middle, and ring fingers up | Switch window with Alt+Tab |
| Hold index and little fingers up | Play or pause media |
| Make no recognized gesture | Idle |

Extended gestures must be held for approximately 0.65 seconds before activation. Action cooldowns prevent immediate repeated commands. Pinch gestures use separate press and release thresholds, so the hand must open enough before the pinch can trigger again.

## Saved Screenshots

Screenshots are automatically saved in the following project folder:

```text
Screenshots/
```

Each screenshot uses a timestamped filename such as:

```text
screenshot_20261121_110000.png
```

## Technologies Used

- Python
- OpenCV
- MediaPipe Tasks Vision
- PyAutoGUI
- NumPy

## Project Structure

```text
AI-Virtual-Mouse/
|-- main.py                 # 2.0 application logic and gesture recognition
|-- requirements.txt        # Python dependencies
|-- hand_landmarker.task    # MediaPipe hand-landmarker model
|-- Screenshots/            # Generated screenshot images
|-- README.md               # Project documentation
`-- .venv/                  # Optional local virtual environment
```

If `hand_landmarker.task` is missing, the application downloads it automatically when `main.py` starts.

## System Requirements

- Windows 10 or Windows 11
- Python 3.10, 3.11, or 3.12
- A working webcam
- Internet connection for the first model download
- Camera permission enabled for desktop applications

Python 3.12 is used in the included virtual environment, but a compatible virtual environment can also be created manually.

## Installation

Open a terminal in the project directory:

```powershell
cd "C:\Users\MITHUN KC\OneDrive\Desktop\AI-Virtual-Mouse"
```

### 1. Create a virtual environment

```powershell
py -m venv .venv
```

### 2. Activate the virtual environment

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command Prompt:

```bat
.venv\Scripts\activate.bat
```

If PowerShell blocks activation, allow local scripts for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then activate the environment again.

### 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

The dependencies include:

```text
opencv-python>=4.8,<5
mediapipe>=0.10.14,<0.11
pyautogui>=0.9.54,<1
numpy>=1.26,<3
```

## Run AI Virtual Mouse 2.0

After activating the virtual environment:

```powershell
python main.py
```

The application will:

1. Download the MediaPipe model if it is not already present.
2. Open the webcam.
3. Start detecting a maximum of one hand.
4. Open a window titled **AI Virtual Mouse 2.0**.
5. Display the current gesture mode, FPS, and gesture hint.
6. Begin moving the cursor and applying gestures.

Keep the camera window in view and press `Q` to stop the application.

## How It Works

1. OpenCV captures a frame from the webcam.
2. The frame is horizontally mirrored so movement feels natural.
3. MediaPipe detects 21 hand landmarks.
4. The application compares landmark positions to determine which fingers are raised.
5. Thumb-index and thumb-middle distances detect pinch gestures.
6. Raised finger combinations select scroll, volume, Copilot, screenshot, and media actions.
7. The index-finger position is mapped to the screen dimensions.
8. Cursor movement uses adaptive smoothing before PyAutoGUI moves the mouse.
9. Hold gestures run a 0.65-second confirmation timer and share action cooldown protection.
10. OpenCV overlays the hand landmarks, status, FPS, and gesture hint on the camera preview.

## Configuration

The following settings can be changed near the top of `main.py`:

```python
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

BASE_SMOOTHING = 0.25
MIN_SMOOTHING = 0.25
MAX_SMOOTHING = 0.75

PINCH_THRESHOLD = 0.055
RELEASE_THRESHOLD = 0.085
CLICK_COOLDOWN = 0.45

SCROLL_SENSITIVITY = 0.015
MAX_SCROLL_STEPS = 5

GESTURE_HOLD_SECONDS = 0.65
ACTION_COOLDOWN = 1.2
VOLUME_STEP_COOLDOWN = 0.16
VOLUME_MOVEMENT_THRESHOLD = 0.025

COPILOT_URI = "ms-copilot:"
```

Configuration guidance:

- `CAMERA_INDEX`: Change this if the wrong camera is selected.
- `FRAME_WIDTH` and `FRAME_HEIGHT`: Adjust the webcam frame resolution.
- `BASE_SMOOTHING`, `MIN_SMOOTHING`, and `MAX_SMOOTHING`: Control adaptive cursor movement smoothing.
- `PINCH_THRESHOLD`: Lower values require a tighter pinch.
- `RELEASE_THRESHOLD`: Controls how far the fingers must separate to release a pinch.
- `CLICK_COOLDOWN`: Minimum time between generated clicks.
- `SCROLL_SENSITIVITY`: Lower values make vertical scrolling more sensitive.
- `MAX_SCROLL_STEPS`: Maximum number of scroll steps generated per movement.
- `GESTURE_HOLD_SECONDS`: Required hold time for advanced gestures.
- `ACTION_COOLDOWN`: Minimum time between repeated advanced actions.
- `VOLUME_STEP_COOLDOWN`: Minimum interval between volume adjustments.
- `VOLUME_MOVEMENT_THRESHOLD`: Minimum palm movement required for a volume step.
- `COPILOT_URI`: Windows URI used to launch the installed Copilot desktop application.

## Troubleshooting

### Camera is unavailable

Make sure no other application is using the webcam and verify that Windows camera access is enabled:

```text
Settings > Privacy & security > Camera
```

If the wrong camera is opened, try changing `CAMERA_INDEX` in `main.py`:

```python
CAMERA_INDEX = 1
```

### MediaPipe model download fails

Check the internet connection and verify that `hand_landmarker.task` is in the project directory. If needed, delete the incomplete model file and run `python main.py` again.

### `pyautogui` cannot control the mouse

Run the terminal with normal desktop user permissions. Security software or restricted desktop environments may block mouse automation.

### Gestures are not detected consistently

- Use bright, even lighting.
- Keep the entire hand visible.
- Keep a moderate distance from the webcam.
- Avoid complex or high-motion backgrounds.
- Move your hand slowly while testing.

### Copilot does not open

Make sure the Microsoft Copilot desktop app is installed and that the `ms-copilot:` URI is registered by Windows. The application cannot launch Copilot through this URI if it is not registered.

### Screenshots are not saved

Verify that the project directory is writable. The application creates a `Screenshots` folder automatically when the little-finger gesture is first triggered.

### The volume does not change

Use the open-palm gesture and move your hand clearly up or down. Windows system audio controls must be available, and another application must not be overriding or locking audio keys.

### PowerShell activation is blocked

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the virtual environment for that terminal session.

## Safety

PyAutoGUI is configured with a failsafe. Move the mouse to the top-left screen corner to stop a run immediately if the cursor becomes difficult to control.

The application processes webcam frames locally and does not upload them to a server.

## Development Commands

Check that dependencies are installed:

```powershell
pip show opencv-python mediapipe pyautogui numpy
```

List outdated packages:

```powershell
pip list --outdated
```

Deactivate the virtual environment:

```powershell
deactivate
```

## Future Improvements

- Drag-and-drop gesture
- Double-click gesture
- Adjustable sensitivity from a settings panel
- Support for both hands
- Mouse-scroll calibration
- Gesture activity notifications
- Executable package for Windows

## License

No license has been included in this repository. Add a `LICENSE` file if you plan to distribute or share the project.
