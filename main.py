import cv2
import numpy as np
import os
import mediapipe as mp
import pyautogui

from gesture_enum import Gesture
from gesture_recognizer import GestureRecognizer

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


SCROLL_SPEED=50
# --- KOLORY ---
KOLOR_BIALY = (255, 255, 255)
KOLOR_KLIK = (0, 255, 255)
KOLOR_KLAWIATURA = (255, 0, 255)
KOLOR_RYSOWANIE = (0, 0, 255)
KOLOR_PRAWY_KLIK = (255, 0, 0)
KOLOR_KROPKI_PRAWA = (0, 255, 0)

# --- MODEL ---
base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2
)

detector = vision.HandLandmarker.create_from_options(options)


cap = cv2.VideoCapture(0)
WINDOW_NAME = 'Gesty - MediaPipe NEW'

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 800, 600)

keyboard_triggered = False
click_triggered = False
right_click_triggered = False
drawing_active = False
enter_triggered = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    result = detector.detect(mp_image)

    status_label = "STATUS: Oczekiwanie"
    action_text = ""
    action_color = KOLOR_BIALY

    if result.hand_landmarks:
        for hand in result.hand_landmarks:
            lm = hand

            cx = int(lm[0].x * w)
            hand_type = "left" if cx < w // 2 else "right"

            # =========================
            # ✋ LEWA RĘKA = GESTY
            # =========================
            if hand_type == "left":

                gesture = GestureRecognizer.recognize(lm)

                if gesture == Gesture.Fist:
                    action_text = " (Klik)"
                    action_color = KOLOR_KLIK

                    if not click_triggered:
                        pyautogui.click()
                        click_triggered = True

                if gesture == Gesture.Victoria:

                    action_text = " (Prawy Klik)"

                    action_color = KOLOR_PRAWY_KLIK

                    if not right_click_triggered:
                        pyautogui.click(button="right")

                        right_click_triggered = True

                if gesture == Gesture.Essa:

                    action_text = " (Klawiatura)"

                    action_color = KOLOR_KLAWIATURA

                    if not keyboard_triggered:
                        os.startfile("osk.exe")

                        keyboard_triggered = True

                elif gesture == Gesture.Drawing:

                    action_text = " (Rysowanie)"

                    action_color = KOLOR_RYSOWANIE

                    if not drawing_active:
                        pyautogui.mouseDown()

                        drawing_active = True



                elif gesture == Gesture.Open:
                    action_text = " (Reset)"
                    action_color = KOLOR_BIALY
                    keyboard_triggered = False

                    click_triggered = False

                    right_click_triggered = False

                    enter_triggered = False

                    if drawing_active:
                        pyautogui.mouseUp()

                        drawing_active = False

                elif gesture == Gesture.Okay:
                    action_text = " (Kciuk w gore)"
                    action_color = KOLOR_RYSOWANIE
                    pyautogui.scroll(SCROLL_SPEED)

                elif gesture == Gesture.NotOkay:
                    action_text = " (Kciuk w dol)"
                    action_color = KOLOR_RYSOWANIE
                    pyautogui.scroll(-SCROLL_SPEED)

                elif gesture == Gesture.Undefined:
                    action_text = " (Nieznany)"
                    action_color = KOLOR_BIALY
                # py = int(lm[8].y * h)
                #
                # cv2.circle(frame, (px, py), 12, KOLOR_KROPKI_PRAWA, -1)

    # --- UI ---
    cv2.rectangle(frame, (0, 0), (w, 60), (30, 30, 30), -1)

    cv2.putText(frame, action_text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, action_color, 2)

    cv2.imshow(WINDOW_NAME, frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()