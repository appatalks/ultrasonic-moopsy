#!/usr/bin/env python3
import argparse
import time
import os

import matplotlib
# matplotlib.use('Agg')  # headless Matplotlib backend
matplotlib.use('Qt5Agg')  # GUI Matplotlib backend
import matplotlib.pyplot as plt

from robot_hat import Ultrasonic, Pin, Music

# Ultrasonic pins
TRIG_PIN = "D1"
ECHO_PIN = "D0"

# Distance threshold for warning
WARNING_DISTANCE = 10.0

# Number of measurements per batch
NUM_READINGS = 90

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

        # Show a quick ASCII bar
        bar_len = min(int(dist_val // 2), 50)
        print(f"{dist_val:5.1f} cm | {'#' * bar_len}")    

        # If below the threshold, print a warning and play sound
        if 0 < dist_val < WARNING_DISTANCE:
            print(f"*** WARNING: Object is within {WARNING_DISTANCE} cm! ***")
            # Play the warning sound (blocking)
            music_obj.sound_play(WARNING_SOUND, volume=100)

        data.append((i, dist_val))
        time.sleep(0.3)

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
    sensor = Ultrasonic(Pin(TRIG_PIN), Pin(ECHO_PIN))
    music_obj = Music()

    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    distances = []
    indices = []

    line, = ax.plot([], [], marker='o', linestyle='-')
    ax.set_ylim(0, 100)  # Set an upper bound for distance, adjust as needed
    ax.set_xlim(0, 200)  # Set initial x-axis range
    ax.set_xlabel("Reading Index")
    ax.set_ylabel("Distance (cm)")
    ax.set_title("Real-Time Ultrasonic Readings")

    i = 0
    while True:  # Infinite loop for continuous readings
        dist = sensor.read()
        # dist = sensor.read() or 0
        
        bar_length = min(int(dist // 2), 50)  # scale down
        print(f"Distance: {dist:>4} cm | " + "#"*bar_length)
        time.sleep(0.3)

        if dist is None:
            dist_val = 0.0
            # print(f"Reading {i + 1}: None")
        else:
            dist_val = dist
            # print(f"Reading {i + 1}: {dist_val:.2f} cm")

        if 0 < dist_val < WARNING_DISTANCE:
            print("*** WARNING ***")
            music_obj.sound_play(WARNING_SOUND, volume=100)

        distances.append(dist_val)
        indices.append(i + 1)
        i += 1

        # Sliding window: Keep only the last 200 readings (optional)
        if len(distances) > 200:
            distances.pop(0)
            indices.pop(0)

        # Update the plotted data
        line.set_xdata(indices)
        line.set_ydata(distances)

        # Expand x-axis and y-axis limits dynamically if needed
        ax.set_xlim(0, max(200, i + 10))
        ax.set_ylim(0, max(100, dist_val + 10))

        plt.draw()
        plt.pause(0.1)  # Allow the plot to update

        time.sleep(0.3)  # Reading interval

if __name__ == "__main__":
    main()
