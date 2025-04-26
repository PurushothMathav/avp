# Advanced Video Processor

A powerful, multi-threaded video processing tool that automates common video file operations, including MKV to MP4 conversion, subtitle extraction, and audio codec fixing.

![Video Processor Banner](https://img.shields.io/badge/Advanced-Video%20Processor-blue)
![Python Version](https://img.shields.io/badge/Python-3.6%2B-brightgreen)
![FFmpeg Required](https://img.shields.io/badge/Requires-FFmpeg-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Features

- **MKV to MP4 Conversion**: Automatically converts MKV files to more widely-compatible MP4 format
- **Subtitle Extraction**: Detects and extracts embedded subtitles to SRT files
- **Audio Codec Fixing**: Identifies and re-encodes non-AAC audio to the AAC codec for better compatibility
- **Multi-threaded Processing**: Optimizes performance by utilizing multiple CPU cores
- **Professional UI**: Color-coded terminal interface with progress tracking
- **Detailed Reporting**: Comprehensive processing reports with file-by-file details

## 🖼️ Screenshots

![Application Interface](https://raw.githubusercontent.com/PurushothMathav/avp/refs/heads/main/Screenshot%202025-04-26%20133310.png)

*Note: Replace with actual screenshot when available*

## 🔧 Requirements

- Python 3.6 or higher
- FFmpeg installed and available in system PATH
- Required Python packages (see Installation)

## 📥 Installation

1. **Clone the repository**

```bash
git clone https://github.com/PurushothMathav/avp.git
cd avp
```

2. **Install required Python packages**

```bash
pip install colorama tqdm tabulate psutil
```

3. **Install FFmpeg**

- **Windows**:
  - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - Add to your system PATH

- **macOS**:
  ```bash
  brew install ffmpeg
  ```

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update
  sudo apt install ffmpeg
  ```

## 🚀 Usage

1. **Place your video files in the `videos` folder**

```bash
mkdir -p videos
# Copy your video files to the videos folder
```

2. **Run the script**

```bash
python avp.py
```
or

```
run avp-portable.bat file
```

3. **View the results**
   - Real-time progress is displayed in the terminal
   - A detailed report is generated at the end of processing
   - A complete log is saved to `video_processing_report.txt`

## ⚙️ Configuration

Edit the following variables at the top of `main.py` to customize behavior:

```python
# Folder containing your video files
INPUT_FOLDER = "videos"  # Change this to your preferred input directory

# Number of processing threads
NUM_THREADS = max(1, multiprocessing.cpu_count() - 2)  # Automatically set based on CPU
```

## 📊 Processing Report

The tool generates a detailed report after processing that includes:

- **Summary Statistics**:
  - Total files processed
  - Number of MKV files converted
  - Number of subtitles extracted
  - Number of audio tracks fixed
  - Total processing time
  - Success rate

- **File Details**:
  - Resolution
  - Duration
  - Original and final file sizes
  - Actions performed on each file

- **Error Log**: Any errors encountered during processing

## 🔄 Processing Workflow

1. **File Analysis**: Each video file is analyzed to determine its format, codecs, and structure
2. **Format Conversion**: MKV files are converted to MP4 format
3. **Subtitle Extraction**: If subtitles are detected, they are extracted to SRT files
4. **Audio Processing**: Non-AAC audio is re-encoded to AAC for better compatibility
5. **Progress Tracking**: Real-time progress is displayed in the terminal
6. **Reporting**: A comprehensive report is generated and saved

## 🛠️ Advanced Features

### Custom FFmpeg Parameters

For advanced users, you can modify the FFmpeg parameters in the code to customize:

- Video encoding options
- Audio bitrate settings
- Subtitle format preferences
- Stream mapping options

### Batch Processing

The tool is designed for batch processing - simply place multiple files in the input folder, and they will all be processed in a single run.

## 🤝 Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [FFmpeg](https://ffmpeg.org/) for the powerful video processing backend
- [tqdm](https://github.com/tqdm/tqdm) for progress bar functionality
- [colorama](https://github.com/tartley/colorama) for cross-platform colored terminal text

## 📞 Contact

For questions, feedback, or support, please open an issue on the GitHub repository.

---

**Advanced Video Processor** - Making video file management easier and faster
