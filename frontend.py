# ============================================================
#  iLert — Drowsiness Detection Frontend  (Kivy GUI)
#
#  This file builds the user-facing interface.  Students do NOT
#  need to understand Kivy to follow the workshop — this is
#  provided as a pre-built UI wrapper around the detection logic.
# ============================================================


#pip install -r requirements.txt

import os
import threading
import time

import cv2
import mediapipe as mp
import pygame

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex
from kivy.graphics.texture import Texture

# ── Window Settings ──────────────────────────────────────────
Window.size = (420, 700)
Window.clearcolor = get_color_from_hex("#0D0D0D")     # Near-black background

# ── Colour Palette ───────────────────────────────────────────
CLR_ACCENT   = get_color_from_hex("#6C63FF")           # Soft purple
CLR_DANGER   = get_color_from_hex("#FF4C4C")           # Red accent (alert)
CLR_SUCCESS  = get_color_from_hex("#34D399")           # Green (active)
CLR_TEXT     = get_color_from_hex("#F0F0F0")           # Off-white text
CLR_MUTED    = get_color_from_hex("#9CA3AF")           # Grey subtext

# ── Audio Setup ──────────────────────────────────────────────
pygame.mixer.init()
ALARM_PATH = os.path.join(os.path.dirname(__file__), "alarm.mp3")


def play_alarm():
    """Load and play the alarm sound file."""
    pygame.mixer.music.load(ALARM_PATH)
    pygame.mixer.music.play()


# ── Styled Rounded Button ───────────────────────────────────
class RoundedButton(Button):
    """A custom Kivy Button with rounded corners and accent styling."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = CLR_ACCENT
        self.color = CLR_TEXT
        self.font_size = 18
        self.bold = True
        self.size_hint_y = None
        self.height = 56
        self.border = (0, 0, 0, 0)


# ── Main Camera Widget ──────────────────────────────────────
class CameraWidget(BoxLayout):
    """
    Root widget that contains:
      • Title bar
      • Live camera preview
      • Status label
      • Start / Stop button
    Detection runs on a background thread so the UI stays responsive.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [16, 20, 16, 20]
        self.spacing = 14

        # ── Title ────────────────────────────────────────────
        title = Label(
            text="[b]Drowsy Detection[/b]",
            markup=True,
            font_size=28,
            color=CLR_TEXT,
            size_hint_y=None,
            height=40,
        )
        subtitle = Label(
            text="Drowsiness Detection System",
            font_size=13,
            color=CLR_MUTED,
            size_hint_y=None,
            height=22,
        )
        self.add_widget(title)
        self.add_widget(subtitle)

        # ── Camera Preview ───────────────────────────────────
        self.camera_widget = Image(
            size_hint=(1, 1),
        )
        self.add_widget(self.camera_widget)

        # ── Status Label ─────────────────────────────────────
        self.status_label = Label(
            text="Tap the button to begin monitoring",
            font_size=14,
            color=CLR_MUTED,
            size_hint_y=None,
            height=28,
        )
        self.add_widget(self.status_label)

        # ── Toggle Button ────────────────────────────────────
        btn_wrap = AnchorLayout(
            anchor_x="center",
            size_hint_y=None,
            height=60,
        )
        self.button = RoundedButton(text="▶  Start Monitoring")
        self.button.bind(on_press=self.toggle_camera)
        btn_wrap.add_widget(self.button)
        self.add_widget(btn_wrap)

        # ── Detection State ──────────────────────────────────
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
        self.running = False
        self.alert_triggered = False
        self.both_eyes_closed_start_time = None
        self.alert_threshold = 1          # seconds
        self.opencv_capture = None

    # ── Camera Toggle ────────────────────────────────────────
    def toggle_camera(self, _instance):
        """Start or stop the camera and detection thread."""
        if self.running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        """Activate the Kivy camera preview and launch the detection thread."""
        self.running = True
        self.alert_triggered = False

        # Update UI
        self.button.text = "■  Stop Monitoring"
        self.button.background_color = CLR_DANGER
        self._update_status("Monitoring active — keep your eyes on screen", CLR_SUCCESS)

        # Start OpenCV capture and schedule processing on the main thread
        self.opencv_capture = cv2.VideoCapture(0)
        self._detect_event = Clock.schedule_interval(self._run_detection, 1.0 / 30.0)

    def stop_camera(self):
        """Release the camera and reset the UI."""
        self.running = False

        if hasattr(self, '_detect_event'):
            self._detect_event.cancel()

        if self.opencv_capture:
            self.opencv_capture.release()

        self.button.text = "▶  Start Monitoring"
        self.button.background_color = CLR_ACCENT
        self._update_status("Monitoring stopped", CLR_MUTED)

    # ── Detection Loop ───────────────────────────────────────
    def _run_detection(self, dt):
        """
        Reads a frame from the webcam, runs detection, and updates
        the UI directly on the main Kivy event loop.
        """
        if not self.running or not self.opencv_capture:
            return

        ret, frame = self.opencv_capture.read()
        if not ret:
            return

        try:
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark

                # Draw faint green FaceMesh for a "wow factor"
                faint_green_spec = mp_drawing.DrawingSpec(color=(0, 150, 0), thickness=1, circle_radius=0)
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=results.multi_face_landmarks[0],
                    connections=mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=faint_green_spec
                )

                # Left eye  (top: 159, bottom: 145)
                left_eye_ratio = landmarks[145].y - landmarks[159].y

                # Right eye (top: 386, bottom: 374)
                right_eye_ratio = landmarks[374].y - landmarks[386].y

                # Eye-closure detection
                left_closed  = left_eye_ratio  < 0.015
                right_closed = right_eye_ratio < 0.004
                both_closed  = left_closed and right_closed

                if both_closed:
                    if self.both_eyes_closed_start_time is None:
                        self.both_eyes_closed_start_time = time.time()
                    elif time.time() - self.both_eyes_closed_start_time >= self.alert_threshold:
                        if not self.alert_triggered:
                            self.alert_triggered = True
                            play_alarm()
                            self._update_status("⚠  ALERT: Wake up!", CLR_DANGER)
                else:
                    self.both_eyes_closed_start_time = None
                    if self.alert_triggered:
                        self.alert_triggered = False
                        self._update_status("Monitoring active — keep your eyes on screen", CLR_SUCCESS)

            # Update the texture for the Kivy image directly
            buf = cv2.flip(frame, 0).tobytes()
            shape = frame.shape
            if not hasattr(self, '_video_texture') or \
               self._video_texture.size != (shape[1], shape[0]):
                self._video_texture = Texture.create(size=(shape[1], shape[0]), colorfmt='bgr')
            
            self._video_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # Force UI update by reassigning texture and asking canvas update
            self.camera_widget.texture = None
            self.camera_widget.texture = self._video_texture
            self.camera_widget.canvas.ask_update()

        except Exception as e:
            print(f"Detection error: {e}")

    # ── Helpers ──────────────────────────────────────────────
    def _update_status(self, text, colour):
        """Safely update the status label (must run on main thread)."""
        self.status_label.text = text
        self.status_label.color = colour


# ── App Entry Point ──────────────────────────────────────────
class iLertApp(App):
    """Kivy Application wrapper."""

    title = "Drowsy Detection"

    def build(self):
        return CameraWidget()


if __name__ == "__main__":
    iLertApp().run()
