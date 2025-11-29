# GCL Studio Pro - Professional Video Recording Suite

## 🎥 Overview

GCL Studio Pro is a professional-grade, cross-platform video/audio recording application built with Python. It features GPU-accelerated encoding, multi-track audio recording, real-time audio monitoring, pause/resume functionality, and automatic platform-optimized exports.

## ✨ Features

### 🎬 Video Recording
- **GPU-Accelerated Encoding** - Automatic detection and use of:
  - NVIDIA NVENC (Windows/Linux)
  - AMD AMF (Windows)
  - Apple VideoToolbox (macOS)
  - Fallback to CPU encoding when GPU unavailable
- **Pause/Resume** - Full control over recording timeline
- **High-Quality MP4** - Professional video output

### 🎙️ Multi-Track Audio Recording
- **Microphone Recording** - High-quality stereo audio (44100 Hz)
- **System Audio Capture** - Record desktop audio when supported
- **Dual-Track Export** - Separate mic and system audio files
- **Pause/Resume** - Synchronized with video recording

### 📊 Real-Time Audio Monitoring
- **Live Level Meter** - Visual audio level display
- **Clipping Detection** - Color-coded warnings:
  - 🟢 Green: Normal levels
  - 🟡 Yellow: Approaching clipping
  - 🔴 Red: Clipping warning
- **Non-Blocking** - Runs in background thread

### 📱 Auto-Export for Social Media
- **Original Resolution** - Full-quality master file
- **TikTok Export** - Vertical 1080x1920 optimized
- **YouTube Export** - HD 1920x1080 optimized
- **Automatic Processing** - All exports created on stop

### 🎨 Professional GUI
- **CustomTkinter** - Modern dark theme interface
- **State Indicators** - Visual recording status
- **GPU Encoder Display** - Shows active encoder
- **Export Results** - Display file paths after processing
- **Responsive Design** - Non-blocking operations

## 📋 Requirements

### Python Dependencies
```bash
pip install customtkinter opencv-python pillow sounddevice soundfile numpy
```

### System Requirements
- **FFmpeg** - Required for merging and platform exports
  - Windows: Download from https://ffmpeg.org/download.html
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`

### Optional (for GPU encoding)
- NVIDIA GPU with latest drivers (for NVENC)
- AMD GPU with latest drivers (for AMF)
- Apple Silicon Mac (for VideoToolbox)

### Optional (for system audio)
- **Windows**: Enable "Stereo Mix" in audio settings
- **macOS**: Install BlackHole or Soundflower
- **Linux**: PulseAudio monitor device

## 🚀 Usage

### Starting the Application
```bash
python app.py
```

### Recording Workflow
1. Click **"Content Creator Studio"**
2. Wait for camera preview to load
3. Click **"⬤ Start Recording"** to begin
4. Optional: Click **"⏸ Pause"** to pause, **"▶ Resume"** to continue
5. Click **"⬛ Stop"** to finish
6. Wait for automatic merge and platform exports

### Recording States
- **● IDLE** (Gray) - Ready to record
- **● RECORDING** (Red) - Currently recording
- **● PAUSED** (Yellow) - Recording paused
- **● STOPPED** (Green) - Processing exports

### Output Files
All files are saved in the `recordings/` directory with timestamps:

- `video_YYYYMMDD_HHMMSS.mp4` - Raw video
- `audio_mic_YYYYMMDD_HHMMSS.wav` - Microphone audio
- `audio_system_YYYYMMDD_HHMMSS.wav` - System audio (if available)
- `video_YYYYMMDD_HHMMSS_FINAL.mp4` - Merged video with audio
- `video_YYYYMMDD_HHMMSS_TIKTOK.mp4` - TikTok vertical export
- `video_YYYYMMDD_HHMMSS_YOUTUBE.mp4` - YouTube HD export

## 🏗️ Architecture

### Core Modules

#### `app.py`
Main application and GUI. Handles:
- CustomTkinter interface
- Video capture and display
- Recording state management
- Button controls and status updates

#### `audio_recorder.py`
Multi-track audio recording with pause/resume:
- Microphone recording thread
- System audio recording thread
- Real-time level monitoring
- Thread-safe queue-based recording

#### `video_encoder.py`
GPU encoder detection and video writing:
- Auto-detect best available GPU encoder
- Fallback to CPU encoding
- FFmpeg pipe for GPU encoding
- cv2.VideoWriter for CPU encoding

#### `export_manager.py`
Merging and platform-optimized exports:
- Multi-track audio merging
- TikTok vertical export (1080x1920)
- YouTube HD export (1920x1080)
- FFmpeg command generation

## 🎛️ Advanced Features

### Pause/Resume Recording
- Continuous timeline - no file splits
- Internal buffering maintains sync
- State machine: idle → recording → paused → recording → stopped

### GPU Encoder Selection
Automatically detects and uses:
1. **Windows**: h264_nvenc (NVIDIA) or h264_amf (AMD)
2. **macOS**: h264_videotoolbox (Apple Silicon)
3. **Linux**: h264_nvenc (NVIDIA)
4. **Fallback**: mp4v CPU encoding

### Multi-Track Audio Merging
When both mic and system audio are available:
```bash
ffmpeg -i video.mp4 -i mic.wav -i system.wav \
  -filter_complex "[1:a][2:a]amix=inputs=2:normalize=0[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac output.mp4
```

### Platform Export Specifications

**TikTok Export:**
- Resolution: 1080x1920 (vertical)
- Video: H.264, 3 Mbps
- Audio: AAC, 128 kbps
- Optimized for mobile viewing

**YouTube Export:**
- Resolution: 1920x1080 (HD)
- Video: H.264, 8 Mbps
- Audio: AAC, 192 kbps, 48 kHz
- YUV420p pixel format
- Fast start enabled

## 🐛 Troubleshooting

### No GPU Encoder Detected
- Ensure latest GPU drivers are installed
- Verify FFmpeg is compiled with GPU support
- Check FFmpeg encoders: `ffmpeg -encoders | grep nvenc`

### System Audio Not Recording
- **Windows**: Enable "Stereo Mix" in sound settings
- **macOS**: Install virtual audio device (BlackHole)
- **Linux**: Ensure PulseAudio monitor is available

### FFmpeg Not Found
- Install FFmpeg and add to system PATH
- Verify installation: `ffmpeg -version`

### Audio Clipping
- Reduce microphone input volume in system settings
- Move away from microphone
- Use audio interface with proper gain staging

### Low Frame Rate
- Close other applications using camera
- Reduce preview window size
- Ensure GPU drivers are up to date

## 🔧 Configuration

### Adjusting Video Quality
Edit `video_encoder.py`, line 124:
```python
'-b:v', '5M',  # Change to desired bitrate (e.g., '10M' for higher quality)
```

### Changing Frame Rate
Edit `app.py`, start_recording function:
```python
video_writer = VideoWriterWrapper(video_filename, width, height, fps=20.0)
# Change fps=20.0 to desired frame rate (e.g., fps=30.0)
```

### Audio Sample Rate
Edit `audio_recorder.py`:
```python
sample_rate = 44100  # Change to 48000 for higher quality
```

## 📝 License

This project is provided as-is for educational and professional use.

## 🙏 Credits

Built with:
- CustomTkinter - Modern GUI framework
- OpenCV - Video capture and processing
- FFmpeg - Video encoding and merging
- sounddevice - Cross-platform audio recording
- soundfile - WAV file writing

## 📧 Support

For issues or questions, please check the troubleshooting section or review the debug output in the console.

---

**GCL Studio Pro** - Professional recording made simple.
