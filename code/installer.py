import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
import subprocess
import re

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.process = None  # To manage the download process
        self.is_paused = False

        # Input Label
        self.label_url = tk.Label(root, text="YouTube Video URL:", font=("Arial", 12))
        self.label_url.pack(pady=10)

        # URL Entry Field
        self.entry_url = tk.Entry(root, width=50, font=("Arial", 12))
        self.entry_url.pack(pady=5)

        # Save Path
        self.label_path = tk.Label(root, text="Save Location:", font=("Arial", 12))
        self.label_path.pack(pady=10)

        # Frame to combine path entry and folder icon button
        self.frame_path = tk.Frame(root)
        self.frame_path.pack(pady=5)

        # Save Path Entry
        self.entry_path = tk.Entry(self.frame_path, width=45, font=("Arial", 12))
        self.entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Folder Icon Button
        script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory
        image_path = os.path.join(script_dir, 'folderi.png')  # Build the full path

        self.icon_folder = tk.PhotoImage(file=image_path).subsample(10, 10)
        self.button_browse = tk.Button(self.frame_path, image=self.icon_folder, command=self.browse_path)
        self.button_browse.pack(side=tk.RIGHT, padx=5)



        # Download Button
        self.button_download = tk.Button(root, text="Download Video", font=("Arial", 12), command=self.start_download)
        self.button_download.pack(pady=10)

        # Pause/Resume Button
        self.button_pause = tk.Button(root, text="Pause Download", font=("Arial", 12), command=self.pause_download, state=tk.DISABLED)
        self.button_pause.pack(pady=5)

        # Status Label
        self.label_status = tk.Label(root, text="", font=("Arial", 10), fg="green")
        self.label_status.pack(pady=10)

        # Progress Label
        self.label_progress = tk.Label(root, text="", font=("Arial", 10), fg="white")
        self.label_progress.pack(pady=5)

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
        self.label_status.config(text="Downloading...", fg="white")
        self.label_progress.config(text="")

        # Start the download in a new thread to prevent freezing
        threading.Thread(target=self.download_video, args=(url, save_path)).start()

    def download_video(self, url, save_path):
        try:
            # Build yt-dlp command
            output_template = os.path.join(save_path, "%(title)s.%(ext)s")
            command = ["yt-dlp", "-o", output_template, "--progress-template", "%(progress.downloaded_bytes)s/%(progress.total_bytes)s", url]

            # Run the command and capture output
            self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in self.process.stdout:
                if self.is_paused:
                    self.process.send_signal(subprocess.signal.SIGSTOP)
                    self.label_status.config(text="Paused", fg="orange")
                self.parse_progress(line)

            self.process.wait()
            if self.process.returncode == 0:
                self.label_status.config(text="Download Complete!", fg="green")
                messagebox.showinfo("Success", "The video has been downloaded successfully!")
            else:
                raise Exception("Download failed.")
        except Exception as e:
            self.label_status.config(text="Download Failed!", fg="red")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Re-enable the download button
            self.button_download.config(state=tk.NORMAL)
            self.button_pause.config(state=tk.DISABLED)
            self.is_paused = False
            self.process = None

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
            self.label_status.config(text="Paused", fg="orange")
            self.button_pause.config(text="Resume Download", command=self.resume_download)

    def resume_download(self):
        if self.process and self.is_paused:
            self.is_paused = False
            self.process.send_signal(subprocess.signal.SIGCONT)
            self.label_status.config(text="Downloading...", fg="white")
            self.button_pause.config(text="Pause Download", command=self.pause_download)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
