# YouTube Video Downloader

## Installation
1. Go [here](https://www.ffmpeg.org/download.html), and download ffmpeg required for yt-dlp
2. Go [here](https://github.com/ShionGT/YouTubeVideoDownload/releases), and follow the instruction there

## Overview

This is a simple desktop application that allows you to download YouTube videos by providing a video URL. It converts the YouTube link into a local file, typically in formats like WebM or MP3. The app is built using Python and supports both macOS and Windows operating systems, with separate versions optimized for each platform.

## Features

- Download YouTube videos.
- User-friendly GUI built with CustomTkinter/Tkinter.
- Supports high-quality downloads via yt-dlp.
- Cross-platform: Separate builds for macOS and Windows.

## Usage

1. Launch the application.
2. Paste the YouTube video URL into the input field.
4. Select the download location.
5. Click "Download" and wait for the process to complete.

**Note:** This tool uses third-party libraries to handle downloads. Be aware of YouTube's terms of service regarding video downloading.

## Platforms

- **Windows:** Tested on Windows 11.
- **macOS:** Tested on macOS Ventura.

## Dependencies

The following libraries were used to build this application:

- altgraph==0.17.4
- customtkinter==5.2.2
- darkdetect==0.8.0
- packaging==25.0
- pefile==2024.8.26
- pytube==15.0.0
- pywin32-ctypes==0.2.3
- setuptools==80.9.0
- yt-dlp==2025.8.28.232853.dev0

## Disclaimer

This tool is for educational purposes only. Downloading copyrighted content without permission may violate YouTube's terms of service or local laws. Use responsibly.
