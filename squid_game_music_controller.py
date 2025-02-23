import pygame
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

pygame.mixer.init()

class MusicController:
    def __init__(self):
        self.tracks = {
            'A': 't.mp3',
            'B': 'r.mp3',
            'C': 'g.mp3'
        }
        self.current_track: Optional[str] = None
        self.lock = threading.Lock()
        self.logs = []
        self.is_paused = False
        self.current_volume = 0.7
        self.running = True
        self.view = None
        self.track_start_time = 0.0
        self.total_played = {'A': 0.0, 'B': 0.0, 'C': 0.0}
        pygame.mixer.music.set_volume(self.current_volume)

    def log(self, msg: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        full_msg = f"[{timestamp}] {msg}"
        self.logs.append(full_msg)
        print(full_msg)

    def _log_duration(self, track: str):
        if track and track in self.total_played:
            duration = time.time() - self.track_start_time
            self.total_played[track] += duration
            self.log(f"Played {track} for {duration:.2f} seconds (Total: {self.total_played[track]:.2f}s)")

    def play(self, track: str, loop: int = 0):
        with self.lock:
            if self.current_track:
                self._log_duration(self.current_track)
            
            self.current_track = track
            self.track_start_time = time.time()
            pygame.mixer.music.load(self.tracks[track])
            pygame.mixer.music.play(loop)
        self.log(f"PLAYING {track}")

    def stop(self):
        with self.lock:
            if self.current_track:
                self._log_duration(self.current_track)
            pygame.mixer.music.stop()
            self.current_track = None
        self.log("MUSIC STOPPED")

    def toggle_pause(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.track_start_time = time.time()
            self.is_paused = False
            self.log("MUSIC RESUMED")
        else:
            if self.current_track:
                self._log_duration(self.current_track)
            pygame.mixer.music.pause()
            self.is_paused = True
            self.log("MUSIC PAUSED")

    def watch_tracks(self):
        while self.running:
            with self.lock:
                track = self.current_track
                busy = pygame.mixer.music.get_busy()
                
            if track == 'C' and not busy:
                self._log_duration(track)
                self.log("TRACK C FINISHED. STARTING TRACK A ON LOOP.")
                self.play('A', loop=-1)
            time.sleep(0.5)

    def set_volume(self, volume: float):
        self.current_volume = volume
        pygame.mixer.music.set_volume(volume)
        if self.view:
            self.view.update_volume_display(volume)

class Application(tk.Tk):
    def __init__(self, controller: MusicController):
        super().__init__()
        self.controller = controller
        controller.view = self
        self.title("🎮 Squid Game Music Controller")
        self._configure_styles()
        self._setup_ui()
        self._start_background_tasks()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        width = 800
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.colors = {
            'primary': '#2A2F3D',
            'secondary': '#3D4455',
            'accent': '#FF6B6B',
            'success': '#4CAF50',
            'text': '#FFFFFF',
            'background': '#1A1E24',
            'highlight': '#4A5260'
        }

        self.style.configure('.', background=self.colors['background'])
        self.style.configure('TButton', 
                           font=('Segoe UI', 11),
                           borderwidth=0,
                           padding=12,
                           relief='flat')
        self.style.configure('TLabel',
                           font=('Segoe UI', 10),
                           background=self.colors['background'],
                           foreground=self.colors['text'])

        button_styles = {
            'primary': ('Primary.TButton', self.colors['primary'], '#3D4455'),
            'accent': ('Accent.TButton', self.colors['accent'], '#FF5252'),
            'success': ('Success.TButton', self.colors['success'], '#45A049')
        }

        for style_name, (style, bg, active_bg) in button_styles.items():
            self.style.configure(style,
                               background=bg,
                               foreground=self.colors['text'])
            self.style.map(style,
                          background=[('active', active_bg),
                                      ('disabled', self.colors['secondary'])])

        self.style.configure('TEntry',
                            fieldbackground=self.colors['secondary'],
                            foreground=self.colors['text'],
                            insertcolor=self.colors['text'],
                            bordercolor=self.colors['primary'],
                            lightcolor=self.colors['primary'],
                            darkcolor=self.colors['primary'])

        self.style.configure('Horizontal.TScale',
                            troughcolor=self.colors['secondary'],
                            sliderthickness=15,
                            sliderrelief='flat')

    def _setup_ui(self):
        self.configure(background=self.colors['background'])
        
        main_frame = ttk.Frame(self)
        main_frame.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(pady=(0, 20))
        self.title_label = ttk.Label(header_frame,
                                    text="SQUID GAME MUSIC CONTROLLER",
                                    font=('Segoe UI', 16, 'bold'),
                                    foreground=self.colors['accent'])
        self.title_label.pack()

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(pady=15, fill=tk.X)
        self.status_label = ttk.Label(status_frame,
                                     font=('Segoe UI', 12),
                                     foreground=self.colors['success'])
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.playback_label = ttk.Label(status_frame,
                                       font=('Consolas', 10),
                                       foreground=self.colors['highlight'])
        self.playback_label.pack(side=tk.RIGHT, padx=10)

        control_grid = ttk.Frame(main_frame)
        control_grid.pack(pady=20, fill=tk.BOTH, expand=True)
        
        controls = [
            ('🎶 Loop Music', 'A', 'Primary.TButton', lambda: self.controller.play('A', -1)),
            ('🔴 Red Light!', 'B', 'Accent.TButton', lambda: self._play_with_stop('B')),
            ('🟢 Green Light', 'C', 'Success.TButton', lambda: self._play_with_stop('C')),
            ('⏸️ Pause', None, 'Primary.TButton', self._toggle_pause),
            ('⏹️ Stop', None, 'Primary.TButton', self.controller.stop),
            ('⏱️ Timer', None, 'Primary.TButton', lambda: self.timer_entry.focus())
        ]

        for i, (text, track, style, cmd) in enumerate(controls):
            btn = ttk.Button(control_grid, text=text, style=style, command=cmd)
            row, col = divmod(i, 3)
            btn.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            if 'Pause' in text:
                self.pause_button = btn

        volume_frame = ttk.Frame(main_frame)
        volume_frame.pack(pady=15, fill=tk.X)
        ttk.Label(volume_frame, text="🔊 Volume:").pack(side=tk.LEFT)
        self.volume = tk.DoubleVar(value=self.controller.current_volume*100)
        self.volume_scale = ttk.Scale(volume_frame,
                                     from_=0,
                                     to=100,
                                     variable=self.volume,
                                     command=lambda v: self.controller.set_volume(float(v)/100),
                                     style='Horizontal.TScale')
        self.volume_scale.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.volume_label = ttk.Label(volume_frame, text="70%")
        self.volume_label.pack(side=tk.LEFT)

        timer_frame = ttk.Frame(main_frame)
        timer_frame.pack(pady=15, fill=tk.X)
        ttk.Label(timer_frame, text="⏱️ Set Timer (seconds):").pack(side=tk.LEFT)
        self.timer_entry = ttk.Entry(timer_frame, width=10)
        self.timer_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(timer_frame,
                  text="Start",
                  style='Success.TButton',
                  command=self._set_timer).pack(side=tk.LEFT, padx=5)
        ttk.Button(timer_frame,
                  text="Cancel",
                  style='Accent.TButton',
                  command=self._cancel_timer).pack(side=tk.LEFT)
        
        self.timer_status = ttk.Label(main_frame, font=('Segoe UI', 9))
        self.timer_status.pack(pady=5)

        ttk.Button(main_frame,
                  text="📜 Show Session Logs",
                  style='Primary.TButton',
                  command=self._show_logs).pack(pady=20)

        for col in range(3):
            control_grid.columnconfigure(col, weight=1)

    def _start_background_tasks(self):
        threading.Thread(target=self.controller.watch_tracks, daemon=True).start()
        self._update_ui()
        self._update_playback_time()

    def _update_ui(self):
        track = self.controller.current_track
        status = f"Current Track: {track}" if track else "No Track Playing"
        self.status_label.config(text=status)
        self.after(200, self._update_ui)

    def _update_playback_time(self):
        if pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos() / 1000
            text = f"Playback: {pos:.1f}s"
        else:
            text = "Playback: 0.0s"
        self.playback_label.config(text=text)
        self.after(500, self._update_playback_time)

    def update_volume_display(self, volume: float):
        self.volume_label.config(text=f"{int(volume*100)}%")

    def _toggle_pause(self):
        self.controller.toggle_pause()
        btn_text = "▶️ Resume" if self.controller.is_paused else "⏸️ Pause"
        self.pause_button.config(text=btn_text)

    def _play_with_stop(self, track: str):
        self.controller.stop()
        self.controller.play(track)

    def _set_timer(self):
        try:
            seconds = int(self.timer_entry.get())
            if seconds <= 0: raise ValueError
        except ValueError:
            self.timer_status.config(text="Invalid time entered", foreground=self.colors['accent'])
            return

        self._cancel_timer()
        self.controller.play('A', -1)
        self.timer_cancel_event = threading.Event()

        def countdown():
            for remaining in range(seconds, 0, -1):
                if self.timer_cancel_event.is_set():
                    break
                self.after(0, lambda r=remaining: self.timer_status.config(
                    text=f"Time remaining: {r}s",
                    foreground=self.colors['text']
                ))
                time.sleep(1)
            else:
                self.after(0, lambda: self._play_with_stop('B'))
                self.after(0, lambda: self.timer_status.config(
                    text="Timer expired! Playing Red Light!",
                    foreground=self.colors['accent']
                ))

        threading.Thread(target=countdown, daemon=True).start()

    def _cancel_timer(self):
        if hasattr(self, 'timer_cancel_event') and self.timer_cancel_event:
            self.timer_cancel_event.set()
        self.timer_status.config(text="Timer cancelled", foreground=self.colors['highlight'])

    def _show_logs(self):
        log_win = tk.Toplevel(self)
        log_win.title("📄 Session Logs")
        log_win.configure(background=self.colors['background'])
        
        text = tk.Text(log_win,
                      wrap=tk.WORD,
                      bg=self.colors['secondary'],
                      fg=self.colors['text'],
                      insertbackground=self.colors['text'],
                      font=('Consolas', 10),
                      padx=10,
                      pady=10)
        
        scroll = ttk.Scrollbar(log_win, command=text.yview)
        text.config(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        text.insert(tk.END, '\n'.join(self.controller.logs))
        text.config(state=tk.DISABLED)

    def _on_exit(self):
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.controller.running = False
            self.controller.stop()
            self.destroy()

if __name__ == "__main__":
    controller = MusicController()
    app = Application(controller)
    app.mainloop()
