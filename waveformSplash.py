import board
import busio
import adafruit_ssd1306
import time
import random
import math

def waveform_animation(oled, duration=2.8, speed=0.04, num_points=32, amplitude=28, decay_rate=0.8):
    """
    Displays an animated audio-like waveform on the OLED.
    Args:
        duration: How long the animation should run (in seconds).
        speed: Controls the animation speed (lower is faster).
        num_points: Number of points in the waveform.
        amplitude: Max vertical height of the waveform.
        decay_rate: How quickly peaks decay (0.0 to 1.0, where 1.0 = no decay)
    """
    start_time = time.monotonic()
    offset = 0
    peak_values = [0] * num_points  # Store previous peak values for decay

    while time.monotonic() - start_time < duration:
        oled.fill(0)  # Clear the display
        center_y = oled.height // 2
        x_spacing = oled.width // num_points

        # Generate and draw the waveform
        for i in range(num_points):
            x = i * x_spacing

            # More dynamic randomness (use a combination of sin and random)
            random_factor = random.uniform(0.5, 1.0)  # Randomness between 0.5 and 1.0
            y_offset = int(amplitude * random_factor * math.sin(2 * math.pi * (i / num_points) + offset))

            # Peak decay
            peak_values[i] = max(abs(y_offset) * decay_rate, peak_values[i] * decay_rate)
            y_offset = int(peak_values[i] * (y_offset / abs(y_offset) if y_offset != 0 else 1)) # Apply decayed peak

             # Ensure y stays within bounds.
            y_positive = min(center_y + y_offset, oled.height -1)
            y_negative = max(center_y - y_offset, 0)


            # Draw the waveform (mirrored) and fill
            oled.line(x, center_y, x, y_positive, 1)  # Positive part
            oled.line(x, center_y, x, y_negative, 1)  # Negative part (mirrored)


        oled.show()  # Update the display
        time.sleep(speed)
        offset += 0.3 #increase slightly for faster movement.
