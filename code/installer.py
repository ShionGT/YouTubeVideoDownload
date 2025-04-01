import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
from functools import partial
import yt_dlp


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("600x450")
        self.root.resizable(True, True)
        self.root.configure(bg="#1a0d2b")

        self.process = None
        self.is_paused = False
        self.active_downloads = 0  # Track number of active downloads
        self.lock = threading.Lock()  # Thread-safe state updates

        self._setup_ui()

    def _setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("Neon.TButton",
                        font=("VCR OSD Mono", 12),
                        background="#ff00ff",
                        foreground="white",
                        borderwidth=0,
                        padding=8,
                        relief="flat")
        style.map("Neon.TButton",
                  background=[("active", "#00ffff")])

        style.configure("Neon.TEntry",
                        fieldbackground="#2a1a4a",
                        foreground="white",
                        borderwidth=0,
                        padding=5)

        main_frame = tk.Frame(self.root, bg="#1a0d2b", bd=0)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(main_frame,
                 text="YouTube Video Downloader",
                 font=("VCR OSD Mono", 24),
                 fg="#00ffff",
                 bg="#1a0d2b").pack(pady=(0, 20))

        tk.Label(main_frame,
                 text="Video URL",
                 font=("VCR OSD Mono", 12),
                 fg="#ff00ff",
                 bg="#1a0d2b").pack()
        self.entry_url = ttk.Entry(main_frame,
                                   style="Neon.TEntry",
                                   width=50)
        self.entry_url.pack(pady=5)

        tk.Label(main_frame,
                 text="Destination",
                 font=("VCR OSD Mono", 12),
                 fg="#ff00ff",
                 bg="#1a0d2b").pack()
        path_frame = tk.Frame(main_frame, bg="#1a0d2b")
        path_frame.pack(fill=tk.X, pady=5)

        self.entry_path = ttk.Entry(path_frame,
                                    style="Neon.TEntry")
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(path_frame,
                   text="Browse",
                   style="Neon.TButton",
                   command=self.browse_path).pack(side=tk.RIGHT)

        self.button_download = ttk.Button(main_frame,
                                          text="Download",
                                          style="Neon.TButton",
                                          command=self.start_download)
        self.button_download.pack(pady=15)

        self.button_pause = ttk.Button(main_frame,
                                       text="Pause",
                                       style="Neon.TButton",
                                       command=self.toggle_pause,
                                       state=tk.DISABLED)
        self.button_pause.pack(pady=10)

        self.label_status = tk.Label(main_frame,
                                     text="Ready",
                                     font=("VCR OSD Mono", 10),
                                     fg="#00ffff",
                                     bg="#1a0d2b")
        self.label_status.pack(pady=10)

        self.label_progress = tk.Label(main_frame,
                                       text="",
                                       font=("VCR OSD Mono", 10),
                                       fg="white",
                                       bg="#1a0d2b")
        self.label_progress.pack()

        self._glow_effect()

    def _glow_effect(self):
        colors = ["#ff00ff", "#00ffff", "#ff00ff"]
        current = self.label_status.cget("fg")
        next_color = colors[(colors.index(current) + 1) % len(colors)]
        self.label_status.config(fg=next_color)
        self.root.after(1000, self._glow_effect)

    def browse_path(self):
        if save_path := filedialog.askdirectory():
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, save_path)

    def start_download(self):
        url, save_path = self.entry_url.get(), self.entry_path.get()

        if not url or not save_path:
            messagebox.showerror("Error", "URL and save location required",
                                 parent=self.root)
            return

        with self.lock:
            self.active_downloads += 1
            self._update_ui_state(downloading=True)

        threading.Thread(target=self._download_video,
                         args=(url, save_path), daemon=True).start()

    def _download_video(self, url, save_path):
        try:
            self._update_status("Downloading", "#00ffff")
            ydl_opts = {
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self._progress_hook],
                'quiet': True,
                'noprogress': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self._update_status("Download Complete!", "#00ff00",
                                lambda: messagebox.showinfo("Success", "Download finished!",
                                                            parent=self.root))
        except Exception as e:
            self._update_status(f"Error: {e}", "#ff4444",
                                lambda: messagebox.showerror("Error", f"Download failed: {e}",
                                                             parent=self.root))
        finally:
            with self.lock:
                self.active_downloads -= 1
                if self.active_downloads == 0:
                    self._update_ui_state(downloading=False)

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d['downloaded_bytes']
            percentage = downloaded / total * 100 if total else 0
            self.label_progress.config(text=f"{downloaded:,} / {total:,} bytes | {percentage:.1f}%")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.button_pause.config(text="Resume" if self.is_paused else "Pause")
        self.label_status.config(text="Paused" if self.is_paused else "Downloading",
                                 fg="#ffff00" if self.is_paused else "#00ffff")

    def _update_ui_state(self, downloading):
        with self.lock:
            self.button_download.config(state="disabled" if downloading else "normal")
            self.button_pause.config(state="normal" if downloading else "disabled")
            self.is_paused = False
            if not downloading and self.active_downloads == 0:
                self.button_pause.config(text="Pause")
                self.label_progress.config(text="")
                self.label_status.config(text="Ready", fg="#00ffff")
            elif downloading:
                self.label_status.config(text="Downloading", fg="#00ffff")

    def _update_status(self, text, color, callback=None):
        with self.lock:
            self.label_status.config(text=text, fg=color)
        if callback:
            self.root.after(0, callback)


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()