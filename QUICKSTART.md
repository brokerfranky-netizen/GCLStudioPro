# GCL Studio Pro - Quick Start Guide

## 🚀 Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Linux (RHEL/CentOS):**
```bash
sudo yum install ffmpeg
```

### 3. Verify Installation
```bash
python -c "import customtkinter; import cv2; print('✓ All dependencies installed')"
ffmpeg -version
```

## 🎬 First Recording

### Step 1: Launch Application
```bash
python app.py
```

### Step 2: Open Creator Studio
Click **"Content Creator Studio"** button

### Step 3: Wait for Camera
The camera preview will appear automatically

### Step 4: Check Audio Levels
Speak into your microphone and watch the audio meter:
- 🟢 Green = Good
- 🟡 Yellow = Loud (but OK)
- 🔴 Red = Too loud (clipping)

### Step 5: Start Recording
Click **"⬤ Start Recording"** (red button)

### Step 6: Record Your Content
- The status will show **● RECORDING** in red
- Frame counter updates every second
- Audio meter shows live levels

### Step 7: Optional - Pause/Resume
- Click **"⏸ Pause"** to pause
- Click **"▶ Resume"** to continue
- Timeline remains continuous

### Step 8: Stop Recording
Click **"⬛ Stop"** when finished

### Step 9: Wait for Processing
The app will automatically:
1. Merge audio and video
2. Create TikTok vertical export
3. Create YouTube HD export
4. Display file paths when complete

### Step 10: Find Your Files
Open the `recordings` folder to find:
- `video_YYYYMMDD_HHMMSS_FINAL.mp4` - Main video
- `video_YYYYMMDD_HHMMSS_TIKTOK.mp4` - TikTok version
- `video_YYYYMMDD_HHMMSS_YOUTUBE.mp4` - YouTube version

## 🎯 Pro Tips

### Optimal Audio Levels
- Keep audio meter in green/yellow range
- Red = clipping/distortion
- Adjust mic volume in system settings

### Best Video Quality
- Good lighting improves camera quality
- Keep camera stable
- Close unnecessary applications

### GPU Encoding
- Check console output for encoder used
- "NVENC" or "AMF" or "VideoToolbox" = GPU ✓
- "CPU (mp4v)" = Using CPU (slower)

### System Audio Recording
**Windows:**
1. Right-click speaker icon → Sounds
2. Recording tab
3. Enable "Stereo Mix"
4. Set as default device

**macOS:**
1. Install BlackHole: `brew install blackhole-2ch`
2. Configure in Audio MIDI Setup
3. Create Multi-Output Device

**Linux:**
System audio capture uses PulseAudio monitors (usually works automatically)

## 📊 Understanding the GUI

### Status Indicators
- **Encoder**: Shows which encoder is active
- **● IDLE**: Ready to record
- **● RECORDING**: Currently recording
- **● PAUSED**: Recording paused
- **● STOPPED**: Processing exports

### Audio Meter
- Bar fills based on microphone input level
- Color changes based on volume
- Updates in real-time

### Export Results
After stopping, shows paths to:
- Original merged file
- TikTok export
- YouTube export

## 🔧 Common Issues

### "ffmpeg not found"
- FFmpeg not installed or not in PATH
- Install FFmpeg (see Installation section)

### "No camera detected"
- Camera in use by another app
- Try restarting the application
- Check camera permissions

### "System audio not available"
- Normal on some systems
- Only mic audio will be recorded
- See System Audio Recording section

### "GPU encoder failed"
- Will automatically fall back to CPU
- Update GPU drivers for best performance

### Recording is slow/choppy
- Close other applications
- Reduce preview window size
- Check CPU usage in Task Manager

## 🎓 Advanced Usage

### Custom Export Settings
Edit `export_manager.py` to customize:
- Video bitrates
- Audio quality
- Resolution settings

### Change Frame Rate
Edit `app.py`, line in start_recording():
```python
fps=20.0  # Change to 30.0 or 60.0
```

### Adjust Audio Quality
Edit `audio_recorder.py`:
```python
sample_rate = 44100  # Change to 48000
```

## 📞 Getting Help

1. **Check console output** - Shows detailed debug logs
2. **Review README.md** - Full documentation
3. **Check requirements.txt** - Verify dependencies
4. **Update drivers** - Especially GPU drivers

## ✅ Checklist

Before your first recording:
- [ ] Python dependencies installed
- [ ] FFmpeg installed and in PATH
- [ ] Camera connected and working
- [ ] Microphone connected and working
- [ ] Good lighting setup
- [ ] Stable camera position
- [ ] Closed unnecessary applications

## 🎉 You're Ready!

Start creating professional content with GCL Studio Pro!

---

**Need help?** Check the debug output in the console for detailed information about what's happening.
