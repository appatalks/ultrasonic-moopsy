#!/usr/bin/env python3
import argparse
import time
import os

import matplotlib
matplotlib.use('Agg')  # headless Matplotlib backend
import matplotlib.pyplot as plt

from robot_hat import Ultrasonic, Pin, Music

# Ultrasonic pins
TRIG_PIN = "D1"
ECHO_PIN = "D0"

# Distance threshold for warning
WARNING_DISTANCE = 10.0

# Number of measurements per batch
NUM_READINGS = 60

# Name/path of the sound file you want to play
# Make sure the file is in a format supported by robot_hat (e.g. .wav, .mp3)
# and placed where the HAT can access it (e.g. same folder or a known directory).
WARNING_SOUND = "moopsy_alert.mp3"

def gather_readings(sensor, music_obj, num_readings=NUM_READINGS):
    """
    Collect 'num_readings' from the ultrasonic sensor.
    Print each measurement and play a warning sound if distance < WARNING_DISTANCE.
    """
    data = []
    print(f"\nStarting data collection of {num_readings} readings...")

    for i in range(1, num_readings + 1):
        dist = sensor.read()
        if dist is None:
            dist_val = 0.0
            print(f"Reading {i}: None (timeout)")
        else:
            dist_val = max(dist, 0)
            print(f"Reading {i}: {dist_val:.2f} cm")

        # If below the threshold, print a warning and play sound
        if 0 < dist_val < WARNING_DISTANCE:
            print(f"*** WARNING: Object is within {WARNING_DISTANCE} cm! ***")
            # Play the warning sound (blocking)
            music_obj.sound_play(WARNING_SOUND, volume=100)

        data.append((i, dist_val))
        time.sleep(0.2)

    print("Collection complete.")
    return data

def plot_data(data, round_number=1):
    """
    Saves a 2D plot (index vs. distance) of the collected data, 
    with a date/time in the filename.
    """
    indices = [d[0] for d in data]
    distances = [d[1] for d in data]

    plt.figure(figsize=(8, 4))
    plt.plot(indices, distances, marker='o', linestyle='-')
    plt.title(f"Ultrasonic Readings - Round {round_number}")
    plt.xlabel("Reading Index")
    plt.ylabel("Distance (cm)")
    plt.ylim(bottom=0)
    plt.grid(True)

    # Use time stamp in filename
    timestamp = time.strftime("%Y%m%d_%H%M")
    filename = f"round_{round_number}_{timestamp}.png"
    plt.savefig(filename)
    plt.close()
    print(f"Plot saved as: {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Ultrasonic distance mapping with Robot HAT Music-based sound warnings."
    )
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="If set, prompt after each round. Otherwise, loop continuously.")
    args = parser.parse_args()

    # Initialize ultrasonic sensor
    sensor = Ultrasonic(Pin(TRIG_PIN), Pin(ECHO_PIN))
    print(f"Ultrasonic sensor initialized (TRIG={TRIG_PIN}, ECHO={ECHO_PIN}).")

    # Initialize Music for HAT speaker playback
    music_obj = Music()

    print("Press Ctrl+C at any time to stop.\n")
    round_number = 1

    while True:
        data = gather_readings(sensor, music_obj, NUM_READINGS)
        plot_data(data, round_number)

        if args.interactive:
            choice = input("Would you like to collect another set? (y/n): ").strip().lower()
            if choice not in ("y", "yes"):
                print("Exiting...")
                break
        else:
            print("Continuing automatically. (Ctrl+C to stop)")
        round_number += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
