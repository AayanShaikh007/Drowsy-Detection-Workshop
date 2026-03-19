# ============================================================
#  iLert — Drowsiness Detection Backend
#  Uses OpenCV + MediaPipe Face Mesh to detect closed eyes
#  and plays an alarm when the user appears to fall asleep.
# ============================================================

import os
import time
import cv2                       # OpenCV — camera capture & image processing
import mediapipe as mp           # MediaPipe — pre-trained ML face-mesh model
import pygame                    # Pygame — audio playback for the alarm

# ── Configuration ────────────────────────────────────────────
ALERT_THRESHOLD = 1              # Seconds both eyes must stay closed before alarm
LEFT_EYE_THRESHOLD  = 0.015      # Vertical-distance threshold for the left eye
RIGHT_EYE_THRESHOLD = 0.004      # Vertical-distance threshold for the right eye

# ── Audio Setup ──────────────────────────────────────────────
pygame.mixer.init()

# Build the alarm path relative to *this* script's location
ALARM_PATH = os.path.join(os.path.dirname(__file__), "alarm.mp3")


def play_alarm():
    """Load and play the alarm sound file."""
    pygame.mixer.music.load(ALARM_PATH)
    pygame.mixer.music.play()


# ── MediaPipe Face Mesh Initialization ───────────────────────
# refine_landmarks=True adds iris landmarks for better accuracy
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

# ── Camera Initialization ────────────────────────────────────
cam = cv2.VideoCapture(0)        # 0 = default webcam

# Timer: tracks when both eyes first closed
both_eyes_closed_start_time = None

# ── Main Detection Loop ─────────────────────────────────────
while True:
    success, frame = cam.read()
    if not success:
        continue                 # Skip if the frame wasn't captured

    # Mirror the frame so it feels like looking in a mirror
    frame = cv2.flip(frame, 1)

    # Get frame dimensions (needed to convert normalised → pixel coords)
    frame_h, frame_w, _ = frame.shape

    # MediaPipe expects RGB; OpenCV captures in BGR
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Run the face-mesh model on the current frame
    results = face_mesh.process(rgb_frame)

    # ── Process Detections ───────────────────────────────────
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        # Left-eye vertical landmarks  (top: 159, bottom: 145)
        left_top    = landmarks[159]
        left_bottom = landmarks[145]
        left_eye_ratio = left_bottom.y - left_top.y   # positive when open

        # Right-eye vertical landmarks (top: 386, bottom: 374)
        right_top    = landmarks[386]
        right_bottom = landmarks[374]
        right_eye_ratio = right_bottom.y - right_top.y  # positive when open

        # Draw small circles on the eye landmarks for visual feedback
        for lm in [left_top, left_bottom, right_top, right_bottom]:
            px = int(lm.x * frame_w)
            py = int(lm.y * frame_h)
            cv2.circle(frame, (px, py), 3, (0, 255, 255), -1)  # Yellow dots

        # ── Eye-Closure Check ────────────────────────────────
        left_closed  = left_eye_ratio  < LEFT_EYE_THRESHOLD
        right_closed = right_eye_ratio < RIGHT_EYE_THRESHOLD
        both_closed  = left_closed and right_closed

        # ── Timer Logic ──────────────────────────────────────
        if both_closed:
            if both_eyes_closed_start_time is None:
                # Eyes just closed — start the timer
                both_eyes_closed_start_time = time.time()
            elif time.time() - both_eyes_closed_start_time >= ALERT_THRESHOLD:
                # Eyes have been closed long enough — trigger alert!
                print("ALERT: USER FELL ASLEEP!")
                cv2.putText(frame, "WAKE UP!", (20, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                play_alarm()
                both_eyes_closed_start_time = None  # Reset to avoid spamming
        else:
            # Eyes are open — reset the timer
            both_eyes_closed_start_time = None

    # ── Display the Camera Feed ──────────────────────────────
    cv2.imshow("iLert — Drowsiness Monitor", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    time.sleep(0.05)  # Small delay to smooth out frame rate

# ── Cleanup ──────────────────────────────────────────────────
cam.release()
cv2.destroyAllWindows()
