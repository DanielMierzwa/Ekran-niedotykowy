import cv2
import numpy as np
import os
import mediapipe as mp
import pyautogui

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

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


def is_finger_up(lm, tip, pip):
    return lm[tip].y < lm[pip].y


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
    prawa_info = "Prawa: Brak"

    if result.hand_landmarks:
        for hand in result.hand_landmarks:
            lm = hand

            # --- ROZDZIELENIE RĄK NA PODSTAWIE POZYCJI ---
            cx = int(lm[0].x * w)

            if cx < w // 2:
                hand_type = "left"
            else:
                hand_type = "right"

            # =========================
            # ✋ LEWA RĘKA = GESTY
            # =========================
            if hand_type == "left":
                f_ind = is_finger_up(lm, 8, 6)#Wskazujący
                f_mid = is_finger_up(lm, 12, 10)#Środkowy
                f_ring = is_finger_up(lm, 16, 14)#Serdeczny
                f_pinky = is_finger_up(lm, 20, 18)#Mały

                if not f_ind and not f_mid and not f_ring and not f_pinky:
                    action_text = " (Klik)"
                    action_color = KOLOR_KLIK

                    if not click_triggered:
                        pyautogui.click()
                        click_triggered = True

                elif f_pinky and not f_ind and not f_mid and not f_ring:
                    action_text = " (Klawiatura)"
                    action_color = KOLOR_KLAWIATURA

                    if not keyboard_triggered:
                        os.startfile("osk.exe")
                        keyboard_triggered = True

                elif f_ind and f_pinky and not f_mid and not f_ring:
                    action_text = " (Rysowanie)"
                    action_color = KOLOR_RYSOWANIE

                    if not drawing_active:
                        pyautogui.mouseDown()
                        drawing_active = True

                elif f_ind and f_mid and not f_ring and not f_pinky:
                    action_text = " (Prawy Klik)"
                    action_color = KOLOR_PRAWY_KLIK

                    if not right_click_triggered:
                        pyautogui.click(button="right")
                        right_click_triggered = True

                elif f_ind and not f_mid  and  f_ring and  f_pinky:
                    action_text = " (Enter)"
                    action_color = KOLOR_KLIK

                    if not enter_triggered:
                        pyautogui.scroll(10)
                        enter_triggered = True

                elif f_ind and f_mid and f_ring and f_pinky:
                    keyboard_triggered = False
                    click_triggered = False
                    right_click_triggered = False
                    enter_triggered = False

                    if drawing_active:
                        pyautogui.mouseUp()
                        drawing_active = False
                

            # =========================
            # 👉 PRAWA RĘKA = ŚLEDZENIE
            # =========================
            elif hand_type == "right":
                px = int(lm[8].x * w)
                py = int(lm[8].y * h)

                cv2.circle(frame, (px, py), 12, KOLOR_KROPKI_PRAWA, -1)
                prawa_info = f"Prawa: X={px} Y={py}"

    # --- UI ---
    cv2.rectangle(frame, (0, 0), (w, 60), (30, 30, 30), -1)

    full_status = f"{prawa_info} | {status_label}"
    cv2.putText(frame, full_status, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, KOLOR_BIALY, 2)

    size = cv2.getTextSize(full_status, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
    x2 = 20 + size[0]

    cv2.putText(frame, action_text, (x2, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, action_color, 2)

    cv2.imshow(WINDOW_NAME, frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()