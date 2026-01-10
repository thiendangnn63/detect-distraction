import cv2
import mediapipe as mp
import numpy as np
import time
import keyboard
import random
import os
import sys
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from win11toast import toast

from gaze_math import get_horizontal_ratio, get_vertical_ratio, get_eye_openness
from roasts import MESSAGES
from storage import save_config, load_config

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
        if "required" in relative_path:
            relative_path = os.path.basename(relative_path)
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

MODEL_PATH = get_resource_path('required/face_landmarker.task')

DISTRACTED_THRESHOLD = 15
NOTIFICATION_CD = 10
SLEEP_THRESHOLD = 0.15

TOGGLE_HOTKEY = 'ctrl+shift+h'
RECALIBRATE_HOTKEY = 'ctrl+shift+r'
DEBUG_HOTKEY = 'ctrl+shift+d'

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = vision.FaceLandmarker
FaceLandmarkerOptions = vision.FaceLandmarkerOptions
VisionRunningMode = vision.RunningMode

try:
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1,
        min_face_detection_confidence=0.5,
        min_face_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True
    )
except Exception as e:
    sys.exit()

cap = cv2.VideoCapture(0)
distracted_counter = 0
last_notify = 0
is_active = True 

top_left_x = 0
top_left_y = 0
bottom_right_x = 0
bottom_right_y = 0
x_ratio_range = [0.0, 0.0]
y_ratio_range = [0.0, 0.0]
is_calibrated = False

check_sleep = False
debug_mode = False 

feedback_text = ""
feedback_start_time = 0

saved_data = load_config()
if saved_data:
    x_ratio_range = saved_data["x_range"]
    y_ratio_range = saved_data["y_range"]
    check_sleep = saved_data["check_sleep"]
    debug_mode = saved_data["debug_mode"]
    is_calibrated = True

def toggle_program():
    global is_active
    is_active = not is_active
    state = "RESUMED" if is_active else "PAUSED"
    toast('Hawkeye', f"Tracking {state}")

def trigger_recalibration():
    global is_calibrated, feedback_text
    is_calibrated = False
    feedback_text = "RE-CALIBRATING..."
    toast('Hawkeye', "Calibration Window Opened")

def toggle_debug():
    global debug_mode
    debug_mode = not debug_mode
    state = "VISIBLE" if debug_mode else "HIDDEN"
    toast('Hawkeye', f"Debug Window: {state}")

keyboard.add_hotkey(TOGGLE_HOTKEY, toggle_program)
keyboard.add_hotkey(RECALIBRATE_HOTKEY, trigger_recalibration)
keyboard.add_hotkey(DEBUG_HOTKEY, toggle_debug)

with FaceLandmarker.create_from_options(options) as landmarker:
    while True:
        if not is_active:
            time.sleep(0.5)
            try: 
                cv2.destroyWindow("Hawkeye Tracking")
            except: 
                pass
            continue

        success, frame = cap.read()
        if not success: break
        
        rgb_frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = landmarker.detect_for_video(mp_image, int(time.time() * 1000))

        if detection_result.face_landmarks:
            landmarks = detection_result.face_landmarks[0]
            
            rh = get_horizontal_ratio(landmarks, [362, 263], 473)
            lh = get_horizontal_ratio(landmarks, [33, 133], 468)
            rv = get_vertical_ratio(landmarks, [386, 374], 473)
            lv = get_vertical_ratio(landmarks, [159, 145], 468)
            
            gaze_h = (rh + lh) / 2
            gaze_v = (rv + lv) / 2
            
            r_open = get_eye_openness(landmarks, [386, 374], [362, 263])
            l_open = get_eye_openness(landmarks, [159, 145], [33, 133])
            avg_openness = (r_open + l_open) / 2

            if not is_calibrated:
                ui_frame = cv2.flip(frame, 1)
                
                sleep_txt = "ON" if check_sleep else "OFF"
                debug_txt = "ON" if debug_mode else "OFF"
                color = (0, 0, 0)
                
                cv2.putText(ui_frame, f"Sleep Check (E): {sleep_txt}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(ui_frame, f"Show Window (W): {debug_txt}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                cv2.putText(ui_frame, "1. Look Top-Left -> 'A'", (20, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(ui_frame, "2. Look Bot-Right -> 'S'", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(ui_frame, "3. Press 'D' to Save", (20, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                key = cv2.waitKey(1)
                if key == ord('a'):
                    top_left_x = gaze_h
                    top_left_y = gaze_v
                    feedback_text = "SAVED: TOP-LEFT"
                    feedback_start_time = time.time()
                elif key == ord('s'):
                    bottom_right_x = gaze_h
                    bottom_right_y = gaze_v
                    feedback_text = "SAVED: BOTTOM-RIGHT"
                    feedback_start_time = time.time()
                elif key == ord('e'): 
                    check_sleep = not check_sleep
                    feedback_text = f"SLEEP: {check_sleep}"
                    feedback_start_time = time.time()
                elif key == ord('w'):
                    debug_mode = not debug_mode
                    feedback_text = f"WINDOW: {debug_mode}"
                    feedback_start_time = time.time()
                elif key == ord('d'):
                    x_vals = [top_left_x, bottom_right_x]
                    x_vals.sort()
                    x_vals[0] *= 0.7
                    x_vals[1] *= 1.3
                    y_vals = [top_left_y, bottom_right_y]
                    y_vals.sort()
                    y_vals[0] *= 0.7
                    y_vals[1] *= 1.3
                    
                    x_ratio_range = x_vals
                    y_ratio_range = y_vals
                    save_config(x_ratio_range, y_ratio_range, check_sleep, debug_mode)
                    
                    is_calibrated = True
                    cv2.destroyAllWindows()
                    toast('Hawkeye', "Tracking Started...")
                    continue 

                if time.time() - feedback_start_time < 2.0:
                    cv2.putText(ui_frame, feedback_text, (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
                cv2.imshow("Hawkeye Calibration", ui_frame)

            else:
                is_x_out = gaze_h < x_ratio_range[0] or gaze_h > x_ratio_range[1]
                is_y_out = gaze_v < y_ratio_range[0] or gaze_v > y_ratio_range[1]
                
                is_sleeping = False
                if check_sleep:
                    is_sleeping = avg_openness < SLEEP_THRESHOLD 
                
                if is_x_out or is_y_out or is_sleeping:
                    distracted_counter += 1
                else:
                    distracted_counter = 0

                if distracted_counter >= DISTRACTED_THRESHOLD:
                    cur_time = time.time()
                    if cur_time - last_notify > NOTIFICATION_CD:
                        roast = random.choice(MESSAGES)
                        if is_sleeping: 
                            roast = "WAKE UP! You're leaking aura points."
                        
                        toast('Hawkeye', roast)
                        last_notify = cur_time

                if debug_mode:
                    debug_frame = cv2.flip(frame, 1)
                    h, w, _ = debug_frame.shape

                    box_x1 = int(x_ratio_range[0] * w)
                    box_x2 = int(x_ratio_range[1] * w)
                    box_y1 = int(y_ratio_range[0] * h)
                    box_y2 = int(y_ratio_range[1] * h)
                    
                    color = (0, 255, 0)
                    if distracted_counter > 0: 
                        color = (0, 0, 255)

                    cv2.rectangle(debug_frame, (box_x1, box_y1), (box_x2, box_y2), color, 2)
                    
                    gaze_x = int(gaze_h * w)
                    gaze_y = int(gaze_v * h)
                    cv2.circle(debug_frame, (gaze_x, gaze_y), 8, (0, 255, 255), -1)

                    status = "FOCUSED"
                    if is_sleeping: 
                        status = "SLEEPING"
                    elif distracted_counter > 0: 
                        status = "DISTRACTED"
                    
                    cv2.putText(debug_frame, f"STATUS: {status}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    
                    cv2.imshow("Hawkeye Tracking", debug_frame)
                else:
                    try: 
                        cv2.destroyWindow("Hawkeye Tracking")
                    except: 
                        pass
        if cv2.waitKey(1) == ord('q'): break
        if debug_mode:
            try:
                if cv2.getWindowProperty("Hawkeye Tracking", cv2.WND_PROP_VISIBLE) < 1:
                    debug_mode = False
            except:
                pass

cap.release()
cv2.destroyAllWindows()