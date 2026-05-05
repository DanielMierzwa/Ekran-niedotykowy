# from gesture_enum import Gesture
#
# class GestureRecognizer:
#
#     @staticmethod
#     def is_finger_up(lm, tip, pip):
#         return lm[tip].y < lm[pip].y
#
#     @staticmethod
#     def recognize(lm):
#         f_ind = GestureRecognizer.is_finger_up(lm, 8, 6)#wskazujący
#         f_mid = GestureRecognizer.is_finger_up(lm, 12, 10)#środkowy
#         f_ring = GestureRecognizer.is_finger_up(lm, 16, 14)#serdeczny
#         f_pinky = GestureRecognizer.is_finger_up(lm, 20, 18)#mały palec
#
#         if not f_ind  and not f_mid and not f_ring and not f_pinky:
#             return Gesture.Fist
#         elif f_ind and f_mid and f_ring and f_pinky:
#             return Gesture.Open
#         elif f_ind and f_pinky and not f_mid and not f_ring:
#             return Gesture.Drawing
#         elif f_ind and f_mid and not f_ring and not f_pinky:
#             return Gesture.Victoria
#         elif f_pinky and not f_ind and not f_mid and not f_ring:
#             return Gesture.Essa
#         else:
#             return Gesture.Undefined
from gesture_enum import Gesture
import math

class GestureRecognizer:

    # ========= PODSTAWY =========
    @staticmethod
    def vector(a, b):
        return [b.x - a.x, b.y - a.y]

    @staticmethod
    def normalize(v):
        length = math.sqrt(v[0]**2 + v[1]**2)
        if length == 0:
            return [0, 0]
        return [v[0]/length, v[1]/length]

    @staticmethod
    def dot(v1, v2):
        return v1[0]*v2[0] + v1[1]*v2[1]

    @staticmethod
    def perpendicular(v):
        # obrót o 90°
        return [-v[1], v[0]]

    # ========= PALCE =========
    @staticmethod
    def is_finger_up(lm, tip, pip, mcp, wrist):
        hand_dir = GestureRecognizer.vector(lm[wrist], lm[mcp])
        finger_dir = GestureRecognizer.vector(lm[pip], lm[tip])

        hand_dir = GestureRecognizer.normalize(hand_dir)
        finger_dir = GestureRecognizer.normalize(finger_dir)

        cos_angle = GestureRecognizer.dot(hand_dir, finger_dir)

        return cos_angle > 0.5  # próg można stroić

    # ========= KCIUK =========
    @staticmethod
    def is_thumb_up(lm):
        WRIST = 0
        THUMB_CMC = 1
        THUMB_TIP = 4

        hand_dir = GestureRecognizer.vector(lm[WRIST], lm[THUMB_CMC])
        thumb_dir = GestureRecognizer.vector(lm[THUMB_CMC], lm[THUMB_TIP])

        hand_dir = GestureRecognizer.normalize(hand_dir)
        thumb_dir = GestureRecognizer.normalize(thumb_dir)

        # kierunek prostopadły do dłoni
        perp = GestureRecognizer.perpendicular(hand_dir)
        perp = GestureRecognizer.normalize(perp)

        cos_angle = abs(GestureRecognizer.dot(perp, thumb_dir))

        return cos_angle < 0.7

    @staticmethod
    def thumb_direction_is_up(lm):
        THUMB_CMC = 1
        THUMB_TIP = 4
        thumb_dir = GestureRecognizer.vector(lm[THUMB_CMC], lm[THUMB_TIP])
        thumb_dir = GestureRecognizer.normalize(thumb_dir)
        if thumb_dir[1]<0:
            return True
        else:
            return False


    # ========= ROZPOZNAWANIE =========
    @staticmethod
    def recognize(lm):
        WRIST = 0

        MCP = {
            "ind": 5,
            "mid": 9,
            "ring": 13,
            "pinky": 17
        }

        f_thumb = GestureRecognizer.is_thumb_up(lm)
        f_ind = GestureRecognizer.is_finger_up(lm, 8, 6, MCP["ind"], WRIST)
        f_mid = GestureRecognizer.is_finger_up(lm, 12, 10, MCP["mid"], WRIST)
        f_ring = GestureRecognizer.is_finger_up(lm, 16, 14, MCP["ring"], WRIST)
        f_pinky = GestureRecognizer.is_finger_up(lm, 20, 18, MCP["pinky"], WRIST)
        # DEBUG (opcjonalnie)
        print(f_thumb, f_ind, f_mid, f_ring, f_pinky)

        if not f_thumb and not f_ind and not f_mid and not f_ring and not f_pinky:
            return Gesture.Fist

        elif f_thumb and f_ind and f_mid and f_ring and f_pinky:
            return Gesture.Open

        elif f_thumb and f_ind and not f_mid and not f_ring and f_pinky:
            return Gesture.Drawing

        elif f_ind and f_mid and not f_ring and not f_pinky:
            return Gesture.Victoria

        elif f_thumb and not f_ind and not f_mid and not f_ring and f_pinky:
            return Gesture.Essa

        elif f_thumb and not f_ind and not f_mid and not f_ring and not f_pinky:
            if GestureRecognizer.thumb_direction_is_up(lm):
                return Gesture.Okay
            else:
                return Gesture.NotOkay
        else:
            return Gesture.Undefined