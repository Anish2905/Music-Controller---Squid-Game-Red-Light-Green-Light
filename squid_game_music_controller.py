import pygame
import threading
import time
import tkinter as tk
from tkinter import messagebox

pygame.mixer.init()

TRACK_A = 't.mp3'
TRACK_B = 'r.mp3'
TRACK_C = 'g.mp3'

current_track = None
lock = threading.Lock()

def play_track(track, loop=0):
    """Load and play the specified track with looping option."""
    global current_track
    with lock:
        current_track = track
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(loop)
    print(f"Playing {track}")

def stop_track():
    """Stop any currently playing track."""
    global current_track
    with lock:
        pygame.mixer.music.stop()
        current_track = None
    print("Music stopped")

def track_watcher():
    """Background thread to monitor track C.
    
    When track C finishes playing, it starts track A on loop.
    """
    while True:
        with lock:
            track = current_track
        if track == TRACK_C and not pygame.mixer.music.get_busy():
            print("Track C finished. Starting track A on loop.")
            play_track(TRACK_A, loop=-1)
        time.sleep(0.1)  

def on_pause():
    """Pause the current playback."""
    pygame.mixer.music.pause()
    print("Music paused")

def on_resume():
    """Resume playback if paused."""
    pygame.mixer.music.unpause()
    print("Music resumed")

def update_status():
    """Update the status label with the current track."""
    with lock:
        track = current_track
    status = f"Current track: {track.split('/')[-1]}" if track else "No track playing"
    status_label.config(text=status)
    root.after(100, update_status)

def on_play_a():
    play_track(TRACK_A, loop=-1)

def on_play_b():
    stop_track()
    play_track(TRACK_B)

def on_play_c():
    stop_track()
    play_track(TRACK_C)

def on_exit():
    if messagebox.askokcancel("Exit", "Do you really want to exit?"):
        stop_track()
        root.destroy()

root = tk.Tk()
root.title("Music Controller - Squid Game Red Light, Green Light")
root.geometry("400x300")

status_label = tk.Label(root, text="No track playing", font=("Helvetica", 14))
status_label.pack(pady=20)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Music (Loop)", font=("Helvetica", 12), 
          command=on_play_a, width=20).grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Red Light!!!", font=("Helvetica", 12), 
          command=on_play_b, width=20).grid(row=0, column=1, padx=5, pady=5)

tk.Button(button_frame, text="Green Light", font=("Helvetica", 12), 
          command=on_play_c, width=20).grid(row=1, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Exit", font=("Helvetica", 12), 
          command=on_exit, width=20).grid(row=1, column=1, padx=5, pady=5)

tk.Button(button_frame, text="Pause", font=("Helvetica", 12), 
          command=on_pause, width=20).grid(row=2, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Resume", font=("Helvetica", 12), 
          command=on_resume, width=20).grid(row=2, column=1, padx=5, pady=5)

threading.Thread(target=track_watcher, daemon=True).start()

root.after(100, update_status)
root.mainloop()
