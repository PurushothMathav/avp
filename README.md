# 🎥 Video Audio Fixer & Converter

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)  
![Platform](https://img.shields.io/badge/Platform-Windows%7C2011%20%7C%202010-lightgrey)  
![License](https://img.shields.io/badge/License-Free-brightgreen)  
![Status](https://img.shields.io/badge/Status-Active-success)

## ✨ About the Project

> **Convert MKV to MP4**, ensure **AAC 192kbps** audio, and **preserve subtitles** — now with a **progress bar** 📊 and **multi-threading** ⚡ for maximum speed!

---

## 📂 Folder Structure

```
video_audio_fixer/
├── main.py
├── README.md
└── videos/
```

## 🛠️ Requirements

- Python 3.8+
- FFmpeg installed and added to PATH

### Install Python packages
```
pip install tqdm
```

## 💻 Setup Instructions

1. Install Python 3.8+ 
1.1 Download from [python.org](https://www.python.org/downloads/)
1.2 ✅ Remember to check **"Add Python to PATH"** during installation.
2. Install FFmpeg and add to PATH
2.1 Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2.2 Extract it, then add `bin/` folder to your **System PATH**.
3. Install required libraries: `pip install tqdm`
4. Place your `.mkv` or `.mp4` files inside `/videos/`
5. Run `python main.py`

## ⚙️ How it Works

- Converts MKV to MP4
- Checks audio codec
- Fixes audio to AAC 192k if needed
- Preserves subtitles
- Shows progress bar
- Uses multiple threads

## 🧹 Notes

- Original files are not overwritten
- Temporary files are auto-deleted

---

# ✅ Enjoy faster, cleaner videos!