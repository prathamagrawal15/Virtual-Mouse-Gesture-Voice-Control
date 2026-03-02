# AI Virtual Mouse: Gesture & Voice Control
#
# Multimodal computer control using hand gestures and voice commands.
#
# Features:
# - Gestures: Mouse movement, clicks, scrolling, dragging.
# - Voice: Open apps/websites, check weather, toggle gesture control.
#
# Usage:
# 1. Install required libraries (opencv-python, mediapipe, pyautogui, etc.).
# 2. Run the script.
# 3. Stop with 'q' key or say "exit program".
#
# ==================================================================================

# --- Core Libraries ---
import os
import threading
import time
import datetime

# --- Gesture Control Libraries ---
import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# --- Voice Assistant Libraries ---
import speech_recognition as sr
import pyttsx3
import webbrowser
import requests

# ==================================================================================
# 1. SHARED STATE AND THREADING SETUP
# ==================================================================================

# Disable PyAutoGUI's failsafe to allow moving the cursor to screen corners
pyautogui.FAILSAFE = False

# Threading Events for communication between voice and gesture threads
gesture_active = threading.Event()
gesture_active.set()  # GESTURE CONTROL IS ACTIVE BY DEFAULT
program_running = threading.Event()
program_running.set()  # Set to True initially, program runs until this is cleared.


# ==================================================================================
# 2. VOICE ASSISTANT FUNCTIONALITY (Runs in a separate thread)
# ==================================================================================

def say(text):
    """Converts text to speech."""
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in pyttsx3: {e}")

def takeCommand():
    """Listens for a voice command and returns it as text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for voice command...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in")
            print(f"User said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
        except Exception as e:
            return ""

def get_weather():
    """Fetches and speaks the weather for a location."""
    # --- Your API key has been added ---
    api_key = "511ec161867c876183434f18ec7c457b" 
    
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    try:
        # Try to get location from IP address
        ip_info = requests.get('http://ip-api.com/json/').json()
        city = ip_info.get('city', 'Delhi') # Default to Delhi if city not found
    except requests.exceptions.RequestException:
        say("Could not determine your location. Checking weather for Delhi.")
        city = "Delhi" # Fallback city

    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(complete_url)
        data = response.json()

        if data.get("cod") != 200:
            error_message = data.get("message", "An unknown error occurred.")
            say(f"Sorry, I couldn't fetch the weather. The service reported: {error_message}")
            print(f"Weather API Error: {error_message}")
            return

        main = data.get("main", {})
        weather = data.get("weather", [{}])[0]
        temp = main.get("temp")
        weather_desc = weather.get("description")
        
        if temp and weather_desc:
            say(f"The temperature in {city} is {temp} degrees Celsius with {weather_desc}.")
        else:
            say("Sorry, I received incomplete weather data.")

    except requests.exceptions.RequestException:
        say("Could not connect to the weather service. Please check your internet connection.")
    except KeyError:
        say("Received an unexpected response from the weather service.")


def run_voice_assistant():
    """Main loop for the voice assistant thread."""
    say("Voice and gesture command activated.")

    while program_running.is_set():
        query = takeCommand()
        if not query:
            continue

        if "activate mouse" in query or "start control" in query:
            say("Activating gesture control.")
            gesture_active.set()
        elif "deactivate mouse" in query or "stop control" in query:
            say("Deactivating gesture control.")
            gesture_active.clear()
        elif "exit program" in query or "goodbye" in query:
            say("Goodbye! Closing the application.")
            program_running.clear()
            break
        elif "the time" in query:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            say(f"The current time is {current_time}")
        elif "temperature" in query or "weather" in query:
            get_weather()
        elif "open whatsapp" in query:
            say("Opening WhatsApp desktop app...")
            try:
                os.system("start whatsapp:")
            except Exception as e:
                say("Sorry, I could not open the WhatsApp desktop app. Make sure it is installed.")
                print(f"Error opening WhatsApp: {e}")
        else:
            sites = [["youtube", "https://www.youtube.com"], ["google", "https://www.google.com"], ["instagram", "https://www.instagram.com"], ["wikipedia", "https://www.wikipedia.com"]]
            for site in sites:
                if f"open {site[0]}" in query:
                    say(f"Opening {site[0]}...")
                    webbrowser.open(site[1])
            apps = {"chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe", "notepad": "notepad.exe", "calculator": "calc.exe"}
            for app_name, app_path in apps.items():
                if f"open {app_name}" in query:
                    say(f"Opening {app_name}")
                    try:
                        os.startfile(app_path) if os.path.exists(app_path) else os.system(f"start {app_path}")
                    except Exception as e:
                        say(f"Sorry, I could not open {app_name}.")
                        print(f"Error opening app: {e}")

# ==================================================================================
# 3. GESTURE CONTROL FUNCTIONALITY (Runs in the main thread)
# ==================================================================================

def run_gesture_control():
    """Main loop for gesture detection and mouse control using your original logic."""
    # --- Setup from your original gesture_recognition.py ---
    wScr, hScr = pyautogui.size()
    frameR = 100
    smoothening = 7
    motion_threshold = 2
    scroll_threshold = 40
    click_threshold = 30
    zoom_cooldown = 0.6
    drag_threshold = 30

    plocX, plocY = 0, 0
    clocX, clocY = 0, 0
    last_click_time = 0
    last_zoom_time = 0
    dragging = False

    # --- Mediapipe Hand Model ---
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    # --- Webcam ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        program_running.clear()
        return
    # --- SETTING A MEDIUM WINDOW SIZE ---
    cap.set(3, 960)  # Set width
    cap.set(4, 540)  # Set height

    # --- Main Gesture Loop ---
    while program_running.is_set():
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Display status text on screen
        status_text = "ACTIVE" if gesture_active.is_set() else "INACTIVE"
        status_color = (0, 255, 0) if gesture_active.is_set() else (0, 0, 255)
        cv2.putText(frame, f"GESTURE CONTROL: {status_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        if not gesture_active.is_set():
            cv2.putText(frame, "Say 'Activate Mouse' to resume", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        if results.multi_hand_landmarks:
            handLms = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            lm = handLms.landmark

            if gesture_active.is_set():
                # ----- Finger Coordinates (from your original code) -----
                ix, iy = int(lm[8].x * w), int(lm[8].y * h)      # Index tip
                tx, ty = int(lm[4].x * w), int(lm[4].y * h)      # Thumb tip
                mx, my = int(lm[12].x * w), int(lm[12].y * h)    # Middle tip
                px, py = int(lm[20].x * w), int(lm[20].y * h)    # Pinky tip
                p_base_y = int(lm[17].y * h)                    # Pinky base

                # ----- Cursor Movement (from your original code) -----
                x3 = np.interp(ix, (frameR, w - frameR), (0, wScr))
                y3 = np.interp(iy, (frameR, h - frameR), (0, hScr))
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                if abs(clocX - plocX) > motion_threshold or abs(clocY - plocY) > motion_threshold:
                    pyautogui.moveTo(clocX, clocY)
                plocX, plocY = clocX, clocY

                current_time = time.time()
                thumb_index_dist = np.hypot(ix - tx, iy - ty)
                thumb_middle_dist = np.hypot(mx - tx, my - ty)

                # ----- Drag & Drop (Reverted to your original, efficient code) -----
                if thumb_index_dist < drag_threshold and thumb_middle_dist < drag_threshold:
                    if not dragging:
                        pyautogui.mouseDown()
                        dragging = True
                        cv2.putText(frame, "Dragging...", (10, 290), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 100, 255), 2)
                else:
                    if dragging:
                        pyautogui.mouseUp()
                        dragging = False
                        cv2.putText(frame, "Drag Released", (10, 290), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)


                # ----- Disable other gestures during drag -----
                if not dragging:
                    # ----- Single / Double Click (from your original code) -----
                    if thumb_index_dist < click_threshold:
                        if current_time - last_click_time < 0.4:
                            pyautogui.doubleClick()
                            cv2.putText(frame, "Double Click", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)
                            last_click_time = 0 # Reset to prevent immediate re-click
                        elif current_time - last_click_time > 0.5: # A small gap to register a new click
                             pyautogui.click()
                             cv2.putText(frame, "Single Click", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                             last_click_time = current_time

                    # ----- Zoom In (from your original code) -----
                    if py < p_base_y - 30 and (current_time - last_zoom_time) > zoom_cooldown:
                        pyautogui.scroll(200)
                        cv2.putText(frame, "Zoom In", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        last_zoom_time = current_time

                    # ----- Zoom Out (from your original code) -----
                    elif py > p_base_y + 20 and (current_time - last_zoom_time) > zoom_cooldown:
                        pyautogui.scroll(-200)
                        cv2.putText(frame, "Zoom Out", (10, 170), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        last_zoom_time = current_time

                    # ----- Ultra-Fast Scrolling (from your original code) -----
                    index_tip_y = lm[8].y
                    middle_tip_y = lm[12].y
                    index_middle_dist = abs(index_tip_y - middle_tip_y) * h

                    if index_middle_dist > scroll_threshold:
                        if index_tip_y < middle_tip_y:
                            pyautogui.scroll(200)
                            cv2.putText(frame, "Scrolling Up", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                        elif index_tip_y > middle_tip_y:
                            pyautogui.scroll(-200)
                            cv2.putText(frame, "Scrolling Down", (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # Display the final frame
        cv2.imshow("AI Gesture and Voice Assistant", frame)

        # Exit condition
        if cv2.waitKey(1) & 0xFF == ord('q'):
            program_running.clear()
            break

    # --- Cleanup ---
    cap.release()
    cv2.destroyAllWindows()
    print("Gesture control thread finished.")

# ==================================================================================
# 4. MAIN EXECUTION BLOCK
# ==================================================================================

if __name__ == "__main__":
    print("Starting AI Assistant...")
    voice_thread = threading.Thread(target=run_voice_assistant, daemon=True)
    voice_thread.start()
    run_gesture_control()
    program_running.clear()
    print("Main program shutting down...")
