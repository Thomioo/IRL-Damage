# Screen Health OCR Script
# Requirements: pyautogui, easyocr, pillow
# You must also have Tesseract-OCR installed on your system and its path added to your environment variables.

import pyautogui
import easyocr
from PIL import Image, ImageEnhance
import numpy as np
import time
import matplotlib.pyplot as plt
import keyboard  # For key event handling (requires 'pip install keyboard')

DEBUG = False  # Set to True to view the captured region in real-time

# Specify the region to capture (update these values as needed)
region = (
    525,  # left (X coordinate)
    1000,  # top (Y Coordinate)
    650 - 525,  # width
    1050 - 1000    # height
)

def capture_and_extract_health(region, debug=False):
    reader = easyocr.Reader(['en'], gpu=True)
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    img_disp = None
    # Debounce variables
    last_stable_health = 0
    last_stable_shield = 0
    candidate_health = 0
    candidate_shield = 0
    candidate_since = time.time()
    debounce_time = 1.0  # seconds the value must remain stable
    contrast_value = 2.0  # Adjust this value for more/less contrast
    last_logged_health = 0
    log_file = open('damage_log.txt', 'a')
    paused = False
    print("Press PgDown to pause/unpause health reading.")
    try:
        while True:
            if keyboard.is_pressed('pagedown'):
                paused = not paused
                print("[PAUSED]" if paused else "[UNPAUSED]")
                time.sleep(0.5)  # Debounce key press
            if paused:
                time.sleep(0.1)
                continue
            screenshot = pyautogui.screenshot(region=region)
            img = screenshot.convert('L')  # Convert to grayscale
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_value)  # Increase contrast
            img = img.point(lambda x: 0 if x < 180 else 255, '1')  # Binarize (black and white)
            img = img.convert('L')  # Convert back to grayscale for easyocr compatibility
            frame = np.array(img)
            if debug:
                if img_disp is None:
                    img_disp = ax.imshow(frame, cmap='gray')
                    plt.title('Captured Region (Close window or press Ctrl+C to exit)')
                else:
                    img_disp.set_data(frame)
                plt.pause(0.001)
                # Print mouse position in debug mode
                mouse_x, mouse_y = pyautogui.position()
                print(f"[DEBUG] Mouse position: ({mouse_x}, {mouse_y})")
            # OCR every frame (or every N frames for performance)
            result = reader.readtext(frame)
            # Separate shield and health by x position
            values = []
            for bbox, text, conf in result:
                try:
                    conf_value = float(conf)
                except Exception:
                    conf_value = 0
                if conf_value > 0.5 and text.strip().isdigit():
                    # bbox: [ [x1, y1], [x2, y2], [x3, y3], [x4, y4] ]
                    x_pos = min([point[0] for point in bbox])
                    values.append((x_pos, int(text.strip())))
            values.sort()  # sort by x position
            shield = 0
            health = 0
            if len(values) == 2:
                shield, health = values[0][1], values[1][1]
            elif len(values) == 1:
                health = values[0][1]
            # Cap values
            health = min(health, 100)
            shield = min(shield, 50)
            # Debounce logic
            if (health, shield) != (candidate_health, candidate_shield):
                candidate_health, candidate_shield = health, shield
                candidate_since = time.time()
            elif time.time() - candidate_since >= debounce_time:
                if (last_stable_health, last_stable_shield) != (candidate_health, candidate_shield):
                    # Detect damage taken
                    if candidate_health < last_stable_health:
                        damage = last_stable_health - candidate_health
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        log_msg = f"[{timestamp}] Damage taken: {damage} (from {last_stable_health} to {candidate_health})"
                        print(log_msg)
                        log_file.write(log_msg + '\n')
                        log_file.flush()
                    last_stable_health, last_stable_shield = candidate_health, candidate_shield
            print(f"Shield: {last_stable_shield} | Health: {last_stable_health}")
            time.sleep(0.1)  # Adjust for performance
            # Exit if the plot window is closed
            if not plt.fignum_exists(fig.number):
                break
    finally:
        log_file.close()
        plt.ioff()
        plt.close()

if __name__ == "__main__":
    capture_and_extract_health(region, debug=DEBUG)
