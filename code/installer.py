import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import subprocess
import re

import yt_dlp


class YouTubeDownloaderApp:
    def __init__(self, root):

        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("500x400")
        self.root.resizable(True, True)

        self.process = None  # To manage the download process
        self.is_paused = False

        # Input Label
        self.label_url = tk.Label(root, text="\n\nYouTube Video URL:", font=("Domine", 14))
        self.label_url.pack()

        # URL Entry Field
        self.entry_url = tk.Entry(root, width=50, font=("Domine", 12))
        self.entry_url.pack()

        # Save Path
        self.label_path = tk.Label(root, text="\nSave Location:", font=("Domine", 14))
        self.label_path.pack()

        # Frame to combine path entry and browse button
        self.frame_path = tk.Frame(root)
        self.frame_path.pack()

        # Save Path Entry
        self.entry_path = tk.Entry(self.frame_path, width=40, font=("Domine", 12))
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Browse Button
        self.button_browse = tk.Button(self.frame_path, text="Browse", font=("Domine", 13), command=self.browse_path)
        self.button_browse.pack(side=tk.RIGHT)

        # Download Button
        self.button_download = tk.Button(root, text="Download Video", font=("Domine", 14), command=self.start_download)
        self.button_download.pack(pady=15)

        # Pause/Resume Button
        self.button_pause = tk.Button(root, text="Pause Download", font=("Domine", 14), command=self.pause_download, state=tk.DISABLED)
        self.button_pause.pack(pady=10)

        # Status Label
        self.label_status = tk.Label(root, text="", font=("Domine", 10), fg="pale green")
        self.label_status.pack(pady=10)

        # Progress Label
        self.label_progress = tk.Label(root, text="", font=("Domine", 10), fg="white smoke")
        self.label_progress.pack()

    def browse_path(self):
        save_path = filedialog.askdirectory()
        if save_path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, save_path)

    def start_download(self):
        url = self.entry_url.get()
        save_path = self.entry_path.get()

        if not url:
            messagebox.showerror("Input Error", "Please enter a YouTube URL")
            return
        if not save_path:
            messagebox.showerror("Input Error", "Please select a save location")
            return

        # Disable download button while downloading
        self.button_download.config(state=tk.DISABLED)
        self.button_pause.config(state=tk.NORMAL)
        self.label_status.config(text="Downloading...", fg="white smoke")
        self.label_progress.config(text="")

        # Start the download in a new thread to prevent freezing
        threading.Thread(target=self.download_video, args=(url, save_path)).start()

    def download_video(self, url, save_path):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.label_status.config(text="Download Complete!", fg="green")
            messagebox.showinfo("Success", "The video has been downloaded successfully!")
        except Exception as e:
            self.label_status.config(text="Download Failed!", fg="red")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.button_download.config(state=tk.NORMAL)
            self.button_pause.config(state=tk.DISABLED)
            self.is_paused = False
            self.process = None

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d['downloaded_bytes']
            percentage = (downloaded / total) * 100 if total else 0
            self.label_progress.config(text=f"Progress: {downloaded} / {total} bytes ({percentage:.2f}%)")


    def parse_progress(self, line):
        match = re.search(r"(\d+)/(?:(\d+))", line)
        if match:
            downloaded = int(match.group(1))
            total = int(match.group(2)) if match.group(2) else 0
            percentage = (downloaded / total) * 100 if total > 0 else 0
            self.label_progress.config(text=f"Progress: {downloaded} bytes / {total} bytes ({percentage:.2f}%)")

    def pause_download(self):
        if self.process and not self.is_paused:
            self.is_paused = True
            self.process.send_signal(subprocess.signal.SIGSTOP)
            self.label_status.config(text="Paused", fg="gold")
            self.button_pause.config(text="Resume Download", command=self.resume_download)

    def resume_download(self):
        if self.process and self.is_paused:
            self.is_paused = False
            self.process.send_signal(subprocess.signal.SIGCONT)
            self.label_status.config(text="Downloading...", fg="white smoke")
            self.button_pause.config(text="Pause Download", command=self.pause_download)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()