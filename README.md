# AI Virtual Mouse: Gesture & Voice Control

This project allows you to control your computer using hand gestures and voice commands. It provides a multimodal interface for interacting with your system, including mouse control, application launching, and more.

## Features

### Gesture Control
- **Mouse Movement:** Control the cursor by moving your index finger.
- **Clicking:** Perform single and double clicks.
- **Dragging:** Drag and drop items.
- **Scrolling:** Scroll up and down.
- **Zooming:** Zoom in and out.

### Voice Commands
- **Application Control:** Open and close applications like Notepad, Calculator, and Chrome.
- **Website Navigation:** Open popular websites like YouTube, Google, and Wikipedia.
- **System Control:** Get the current time, check the weather, and exit the program.
- **Toggle Gesture Control:** Activate or deactivate gesture control using voice commands.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/prathamagrawal15/Virtual-Mouse-Gesture-Voice-Control.git
    cd Virtual-Mouse-Gesture-Voice-Control
    ```

2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    **Note on `PyAudio`:** If you encounter issues installing `PyAudio`, you may need to install it manually. You can find wheels for your Python version and system architecture [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio).

## Usage

1.  **Run the script:**
    ```bash
    python final_gesture.py
    ```
2.  The script will start, and you will see a window with your webcam feed.
3.  You can now control your computer using gestures and voice commands.
4.  To stop the program, press the 'q' key or say "exit program".

## Gesture Commands

-   **Move Cursor:** Move your index finger in front of the camera.
-   **Single Click:** Briefly touch your thumb and index finger.
-   **Double Click:** Touch your thumb and index finger twice in quick succession.
-   **Drag & Drop:** Pinch your thumb and index finger together to grab, move your hand, and release to drop.
-   **Scroll Up:** Move your index finger up while keeping your middle finger stationary.
-   **Scroll Down:** Move your middle finger up while keeping your index finger stationary.
-   **Zoom In:** Raise your pinky finger.
-   **Zoom Out:** Lower your pinky finger.

## Voice Commands

-   "activate mouse" / "start control"
-   "deactivate mouse" / "stop control"
-   "exit program" / "goodbye"
-   "what is the time"
-   "what is the temperature" / "what is the weather"
-   "open whatsapp"
-   "open youtube"
-   "open google"
-   "open instagram"
-   "open wikipedia"
-   "open chrome"
-   "open notepad"
-   "open calculator"

## Dependencies

The project uses the following libraries:

-   `opencv-python`
-   `mediapipe`
-   `pyautogui`
-   `numpy`
-   `SpeechRecognition`
-   `pyttsx3`
-   `requests`
-   `pyaudio`
