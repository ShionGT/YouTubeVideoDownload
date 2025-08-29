import customtkinter as ctk
import threading
import yt_dlp
import os
from tkinter import filedialog

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("400x400")
        self.fg_color = "#ff00ff"
        self.bg_color = "#1a0d2b"
        self.root.config(bg=self.bg_color)
        #self.root.iconbitmap("icon.ico")

        self.download_path = ""
        self.active_downloads = 0
        self.download_thread = None
        self.should_cancel = False

        self._setup_ui()

    def _setup_ui(self):
        # Title
        self.screen_title = ctk.CTkLabel(
            master=self.root,
            text="YouTube Downloader",
            font=("Bold", 30),
            text_color="white",
            bg_color=self.bg_color,
        )
        self.screen_title.pack(pady=25, fill="x")

        # URL Entry
        self.entry_url = ctk.CTkEntry(
            master=self.root,
            placeholder_text="Enter YouTube URL",
            font=("Bold", 20),
            width=350,
            height=40,
            bg_color=self.bg_color,
        )
        self.entry_url.pack(pady=5)

        # Directory Label
        self.directory_selected_label = ctk.CTkLabel(
            master=self.root,
            text="No directory selected",
            font=("Bold", 16),
            wraplength=350,
            text_color="white",
            bg_color=self.bg_color,
        )
        self.directory_selected_label.pack(pady=5)

        # Browse Button
        self.browse_button = ctk.CTkButton(
            master=self.root,
            text="Browse",
            font=("Bold", 20),
            text_color="white",
            width=120,
            height=40,
            corner_radius=10,
            border_width=2,
            border_color="white",
            fg_color=self.fg_color,
            bg_color=self.bg_color,
            command=self.browse_directory,
        )
        self.browse_button.pack(pady=5)

        # Download Button
        self.download_button = ctk.CTkButton(
            master=self.root,
            text="Download",
            font=("Bold", 20),
            text_color="white",
            width=120,
            height=40,
            corner_radius=10,
            border_width=2,
            border_color="white",
            fg_color=self.fg_color,
            bg_color=self.bg_color,
            command=self.start_download,
        )
        self.download_button.pack(pady=5)

        # Status Label
        self.current_status_label = ctk.CTkLabel(
            master=self.root,
            text="Ready",
            font=("Bold", 16),
            text_color="white",
            bg_color=self.bg_color,
        )
        self.current_status_label.pack(pady=5)

    def browse_directory(self):
        self.download_path = filedialog.askdirectory()
        if self.download_path:
            self.download_path = os.path.normpath(self.download_path)
            self.directory_selected_label.configure(text=f"Selected: {self.download_path}")
        else:
            self.directory_selected_label.configure(text="No directory selected")

    def start_download(self):
        url = self.entry_url.get()
        if not url or not self.download_path:
            self.current_status_label.configure(text="Invalid URL or save path")
            return

        self.active_downloads += 1
        self.should_cancel = False
        self.download_button.configure(state="disabled")
        self.current_status_label.configure(text="Starting download...")

        # Start download in a separate thread
        self.download_thread = threading.Thread(
            target=self.download_video,
            args=(url, self.download_path),
            daemon=True,
        )
        self.download_thread.start()

    def download_video(self, url, save_path):
        try:
            ydl_opts = {
                "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
                "progress_hooks": [self._progress_hook],
                "quiet": False,
                "noprogress": False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.should_cancel:
                    raise Exception("Download canceled by user")
                ydl.download([url])
            self.root.after(0, lambda: self.current_status_label.configure(text="Download completed"))
        except Exception as e:
            self.root.after(0, lambda: self.current_status_label.configure(text=f"Error: {str(e)}"))
        finally:
            self.active_downloads -= 1
            self.root.after(0, lambda: self.download_button.configure(state="normal"))

    def _progress_hook(self, d):
        if self.should_cancel:
            return
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d["downloaded_bytes"]
            percentage = downloaded / total * 100 if total else 0
            # Update label in the main thread
            self.root.after(
                0,
                lambda: self.current_status_label.configure(
                    text=f"{downloaded:,} / {total:,} bytes | {percentage:.1f}%"
                ),
            )

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Optional: Set dark mode for better visuals
    root = ctk.CTk()
    app = YouTubeDownloader(root)
    root.mainloop()