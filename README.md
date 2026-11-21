# AI Virtual Mouse

AI Virtual Mouse is a Python computer-vision project that controls the Windows mouse using hand gestures captured through a webcam. It uses MediaPipe Hand Landmarker for real-time hand tracking, OpenCV for the camera and visual interface, and PyAutoGUI for cursor and click automation.

The application is optimized for a webcam resolution of 640x480 and moves the cursor based on the position of the index finger.

## Features

- Real-time hand and finger tracking
- Smooth cursor movement
- Left-click gesture
- Right-click gesture
- Vertical scrolling gesture
- Hysteresis-based pinch detection to reduce accidental repeated clicks
- PyAutoGUI failsafe protection
- Webcam preview with hand landmarks and the current gesture mode
- Automatic MediaPipe model download on first launch
- Emergency stop by moving the mouse to a screen corner
- Press `Q` to close the application

## Gesture Controls

| Gesture | Action |
|---|---|
| Raise only the index finger | Move the mouse cursor |
| Pinch the thumb and index finger | Left click |
| Pinch the thumb and middle finger | Right click |
| Raise both index and middle fingers | Scroll |
| Make no recognized gesture | Idle |

The pinch gestures are detected with separate release thresholds, so the hand must open a little before the gesture can be triggered again.

## Technologies Used

- Python
- OpenCV
- MediaPipe Tasks Vision
- PyAutoGUI
- NumPy

## Project Structure

```text
AI-Virtual-Mouse/
|-- main.py                 # Application logic and gesture recognition
|-- requirements.txt        # Python dependencies
|-- hand_landmarker.task    # MediaPipe hand-landmarker model
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

## Run the Project

After activating the virtual environment:

```powershell
python main.py
```

The application will:

1. Download the MediaPipe model if it is not already present.
2. Open the webcam.
3. Start detecting a maximum of one hand.
4. Open a window titled **AI Virtual Mouse**.
5. Begin moving the cursor and applying gestures.

Keep the camera window in view and press `Q` to stop the application.

## How It Works

1. OpenCV captures a frame from the webcam.
2. The frame is horizontally mirrored so movement feels natural.
3. MediaPipe detects 21 hand landmarks.
4. The application compares landmark positions to determine which fingers are raised.
5. Thumb-index and thumb-middle distances detect pinch gestures.
6. The index-finger position is mapped to the screen dimensions.
7. Cursor movement is smoothed before PyAutoGUI moves the mouse.
8. OpenCV overlays the hand landmarks and current mode on the camera preview.

## Configuration

The following settings can be changed near the top of `main.py`:

```python
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
SMOOTHING = 0.25
PINCH_THRESHOLD = 0.055
RELEASE_THRESHOLD = 0.085
CLICK_COOLDOWN = 0.45
SCROLL_SENSITIVITY = 0.015
```

Configuration guidance:

- `CAMERA_INDEX`: Change this if the wrong camera is selected.
- `FRAME_WIDTH` and `FRAME_HEIGHT`: Adjust the webcam frame resolution.
- `SMOOTHING`: Lower values produce smoother movement but increase delay.
- `PINCH_THRESHOLD`: Lower values require a tighter pinch.
- `RELEASE_THRESHOLD`: Controls how far the fingers must separate to release a pinch.
- `CLICK_COOLDOWN`: Minimum time between generated clicks.
- `SCROLL_SENSITIVITY`: Lower values make scrolling more sensitive.

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

### PowerShell activation is blocked

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the virtual environment for that terminal session.

## Safety

PyAutoGUI is configured with a failsafe. Move the mouse to any screen corner to stop a run immediately if the cursor becomes difficult to control.

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
