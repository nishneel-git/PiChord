#Nishad Neelakandan 2025 - PiChord
#If you make improvements, please email them to me at nishadneel@gmail.com

import board
import digitalio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
import time
from analogio import AnalogIn
import busio
import adafruit_ssd1306
import waveformSplash  


# --- Constants ---
i2c = busio.I2C(board.GP17, board.GP16)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
oledLine1X = 0  # Adjusted for longer text

# Joystick Setup
x_axis = AnalogIn(board.GP26)
y_axis = AnalogIn(board.GP28)
center_y = 32583
center_x = 33000
threshold = 16000
joystick_debounce_time = 0.02  # Debounce time for joystick changes.


# MIDI setup
midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1])
midi_channel = 1

# Key setup
keys = [digitalio.DigitalInOut(getattr(board, f"GP{i}")) for i in range(7)]
for key in keys:
    key.direction = digitalio.Direction.INPUT
    key.pull = digitalio.Pull.UP

# Cycle button setup
cycle_button = digitalio.DigitalInOut(board.GP7)
cycle_button.direction = digitalio.Direction.INPUT
cycle_button.pull = digitalio.Pull.UP

# --- Scales and Chords ---
scales = {
    "C major": [(60, 64, 67), (62, 65, 69), (64, 67, 71), (65, 69, 72), (67, 71, 74), (69, 72, 76), (71, 74, 77)],
    "C minor": [(60, 63, 67), (62, 65, 68), (63, 67, 70), (65, 68, 72), (67, 70, 74), (68, 72, 75), (70, 74, 77)],
    "D major": [(62, 66, 69), (64, 67, 71), (66, 69, 73), (67, 71, 74), (69, 73, 76), (71, 74, 78), (73, 76, 79)],
    "D minor": [(62, 65, 69), (64, 67, 70), (65, 69, 72), (67, 70, 74), (69, 72, 76), (70, 74, 77), (72, 76, 79)],
    "E major": [(64, 68, 71), (66, 69, 73), (68, 71, 75), (69, 73, 76), (71, 75, 78), (73, 76, 80), (75, 78, 81)],
    "E minor": [(64, 67, 71), (66, 69, 72), (67, 71, 74), (69, 72, 76), (71, 74, 78), (72, 76, 79), (74, 78, 81)],
    "F major": [(65, 69, 72), (67, 70, 74), (69, 72, 76), (70, 74, 77), (72, 76, 79), (74, 77, 81), (76, 79, 82)],
    "F minor": [(65, 68, 72), (67, 70, 73), (68, 72, 75), (70, 73, 77), (72, 75, 79), (73, 77, 80), (75, 79, 82)],
    "G major": [(67, 71, 74), (69, 72, 76), (71, 74, 78), (72, 76, 79), (74, 78, 81), (76, 79, 83), (78, 81, 84)],
    "G minor": [(67, 70, 74), (69, 72, 75), (70, 74, 77), (72, 75, 79), (74, 77, 81), (75, 79, 82), (77, 81, 84)],
    "A major": [(69, 73, 76), (71, 74, 78), (73, 76, 80), (74, 78, 81), (76, 80, 83), (78, 81, 85), (80, 83, 86)],
    "A minor": [(69, 72, 76), (71, 74, 77), (72, 76, 79), (74, 77, 81), (76, 79, 83), (77, 81, 84), (79, 83, 86)],
    "B major": [(71, 75, 78), (73, 76, 80), (75, 78, 82), (76, 80, 83), (78, 82, 85), (80, 83, 87), (82, 85, 88)],
    "B minor": [(71, 74, 78), (73, 76, 79), (74, 78, 81), (76, 79, 83), (78, 81, 85), (79, 83, 86), (81, 85, 88)],
}
scale_names = list(scales.keys())

# --- Voicings ---
voicings = {
    "N":  [0, 0, 0],
    "E":  [0, 7, 12],
    "W":  [-12, -5, 0],
    "SW": [0, 5, 10],
    "NW": [0, 4, 10],
    "NE": [0, 7, 14],
    "S":  [-12, 4, 7],
    "SE": [0, 5, 9]
}

# --- Voicing Names (for display) ---
voicing_names = {
    "N":  "Unison",
    "E":  "Open (R, 5, 8ve)",
    "W":  "2nd Inv Maj",
    "SW": "Quartal (R, 4, M7)",
    "NW": "Major 7th",
    "NE": "Power Chord +8ve",
    "S":  "1st Inv Maj",
    "SE": "Root, 5th, M6/M9"
}


# --- Initialization ---
current_scale_index = 0
current_scale = scale_names[current_scale_index]
current_voicing = "N"

# Handle Initial Button Press (BEFORE splash screen)
initial_button_state = cycle_button.value
time.sleep(0.1)  # Debounce
if not initial_button_state and not cycle_button.value:
    current_scale_index = (current_scale_index + 1) % len(scale_names)
    current_scale = scale_names[current_scale_index]


key_states = [False] * 7
last_cycle_button_state = cycle_button.value
debounce_time = 0.002
last_release_time = [0] * 7
active_notes = set()

# --- Splash Screen ---
oled.fill(0)
oled.text("Nish Dholi", 8, 10, 1, size=2)
oled.text("2025", 45, 35, 1, size=2)
oled.invert(True)
oled.show()
time.sleep(0.6)
oled.invert(False)
oled.show()
waveformSplash.waveform_animation(oled)  # Display waveform animation

# --- Function to get joystick direction ---
def get_joystick_direction():
    x = x_axis.value
    y = y_axis.value

    # Prioritize Diagonal Checks *FIRST*
    if x > center_x + threshold and y > center_y + threshold:  return "SE"
    elif x < center_x - threshold and y > center_y + threshold: return "SW"
    elif x > center_x + threshold and y < center_y - threshold: return "NE"
    elif x < center_x - threshold and y < center_y - threshold: return "NW"
    # *Then* check cardinal directions
    elif abs(x - center_x) < threshold and abs(y - center_y) < threshold: return "N"
    elif x > center_x + threshold and abs(y - center_y) < threshold:   return "E"
    elif x < center_x - threshold and abs(y - center_y) < threshold:   return "W"
    elif abs(x - center_x) < threshold and y > center_y + threshold:   return "S"
    elif abs(x - center_x) < threshold and y < center_y - threshold:   return "N" #Duplicate
    return "N"  # Default to "N"

# --- Panic Function (All Notes Off) ---
def all_notes_off():
    for note in range(128):
        midi.send(NoteOff(note, 0))
    active_notes.clear()

# --- Display Update Function ---
def update_display():
    oled.fill(0)  # Clear the display
    oled.text(current_scale, oledLine1X, 0, 1, size=2)
    oled.text(voicing_names[current_voicing], oledLine1X, 16, 1, size=1)  # Directly use voicing_names
    oled.show()

update_display() # Initial display

# --- Main loop ---
while True:
    # --- Key cycling ---
    if cycle_button.value != last_cycle_button_state:
        last_cycle_button_state = cycle_button.value
        time.sleep(0.1)  # Debounce
        if not cycle_button.value:
            current_scale_index = (current_scale_index + 1) % len(scale_names)
            current_scale = scale_names[current_scale_index]
            all_notes_off()
            update_display() # Update display after changing scale

    # --- Key presses and releases ---
    for i, key in enumerate(keys):
        if key.value != key_states[i]:
            key_states[i] = key.value
            if not key.value:  # Key pressed
                oled.invert(True)
                chord = scales[current_scale][i]
                voiced_chord = [note + voicings[current_voicing][j] for j, note in enumerate(chord)]
                for note in voiced_chord:
                    if note not in active_notes:
                        midi.send(NoteOn(note, 127))
                        active_notes.add(note)

            else:  # Key released (debounced)
                oled.invert(False)
                if (time.monotonic() - last_release_time[i]) > debounce_time:
                    last_release_time[i] = time.monotonic()
                    chord = scales[current_scale][i]
                    voiced_chord = [note + voicings[current_voicing][j] for j, note in enumerate(chord)]
                    currently_held_notes = set()
                    for j, other_key in enumerate(keys):
                        if j != i and not other_key.value:
                            other_chord = scales[current_scale][j]
                            other_voiced_chord = [n + voicings[current_voicing][k] for k, n in enumerate(other_chord)]
                            currently_held_notes.update(other_voiced_chord)
                    for note in voiced_chord:
                        if note not in currently_held_notes:
                            midi.send(NoteOff(note, 0))
                            if note in active_notes:
                                active_notes.remove(note)

    # --- Joystick Voicing Change ---
    new_voicing = get_joystick_direction()
    time.sleep(0.07)
    if new_voicing != current_voicing:
        if not any(key_states):  # If no keys are pressed
            if new_voicing != current_voicing:
                current_voicing = new_voicing
                update_display()  # Update the display immediately
        else: # Keys are held
            notes_to_turn_off = set()
            notes_to_turn_on = set()

            for i, key in enumerate(keys):
                if not key.value:
                    chord = scales[current_scale][i]
                    old_voiced_chord = [note + voicings[current_voicing][j] for j, note in enumerate(chord)]
                    new_voiced_chord = [note + voicings[new_voicing][j] for j, note in enumerate(chord)]
                    notes_to_turn_off.update(set(old_voiced_chord) - set(new_voiced_chord))
                    notes_to_turn_on.update(set(new_voiced_chord) - set(old_voiced_chord))

            notes_to_turn_off -= notes_to_turn_on

            for note in notes_to_turn_off:
                if note in active_notes:
                    midi.send(NoteOff(note, 0))
                    active_notes.remove(note)

            for note in notes_to_turn_on:
                midi.send(NoteOn(note, 127))
                active_notes.add(note)
            if new_voicing != current_voicing:
                current_voicing = new_voicing  # Update after note changes
                update_display() # Update display after voicing change