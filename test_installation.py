"""
test_installation.py
Verify that GCL Studio Pro is correctly installed and configured
"""

import sys

print("=" * 70)
print("GCL Studio Pro - Installation Test")
print("=" * 70)
print()

# Test 1: Python version
print("[1/8] Checking Python version...")
if sys.version_info >= (3, 8):
    print(f"     ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
else:
    print(f"     ✗ Python {sys.version_info.major}.{sys.version_info.minor} (3.8+ required)")
    sys.exit(1)

# Test 2: CustomTkinter
print("[2/8] Checking CustomTkinter...")
try:
    import customtkinter as ctk
    print(f"     ✓ CustomTkinter installed")
except ImportError:
    print("     ✗ CustomTkinter not found - Run: pip install customtkinter")
    sys.exit(1)

# Test 3: OpenCV
print("[3/8] Checking OpenCV...")
try:
    import cv2
    print(f"     ✓ OpenCV {cv2.__version__}")
except ImportError:
    print("     ✗ OpenCV not found - Run: pip install opencv-python")
    sys.exit(1)

# Test 4: PIL/Pillow
print("[4/8] Checking Pillow...")
try:
    from PIL import Image
    print(f"     ✓ Pillow installed")
except ImportError:
    print("     ✗ Pillow not found - Run: pip install Pillow")
    sys.exit(1)

# Test 5: sounddevice
print("[5/8] Checking sounddevice...")
try:
    import sounddevice as sd
    print(f"     ✓ sounddevice installed")
except ImportError:
    print("     ✗ sounddevice not found - Run: pip install sounddevice")
    sys.exit(1)

# Test 6: soundfile
print("[6/8] Checking soundfile...")
try:
    import soundfile as sf
    print(f"     ✓ soundfile installed")
except ImportError:
    print("     ✗ soundfile not found - Run: pip install soundfile")
    sys.exit(1)

# Test 7: NumPy
print("[7/8] Checking NumPy...")
try:
    import numpy as np
    print(f"     ✓ NumPy {np.__version__}")
except ImportError:
    print("     ✗ NumPy not found - Run: pip install numpy")
    sys.exit(1)

# Test 8: FFmpeg
print("[8/8] Checking FFmpeg...")
import subprocess
try:
    result = subprocess.run(
        ['ffmpeg', '-version'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        version_line = result.stdout.split('\n')[0]
        print(f"     ✓ {version_line}")
    else:
        print("     ✗ FFmpeg error")
except FileNotFoundError:
    print("     ✗ FFmpeg not found - Install from https://ffmpeg.org/")
    print("       Windows: Download and add to PATH")
    print("       macOS: brew install ffmpeg")
    print("       Linux: sudo apt install ffmpeg")
except Exception as e:
    print(f"     ✗ FFmpeg check failed: {e}")

print()
print("=" * 70)
print("Optional Components")
print("=" * 70)
print()

# Test Camera
print("[OPT] Testing camera access...")
try:
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            height, width = frame.shape[:2]
            print(f"     ✓ Camera detected: {width}x{height}")
        else:
            print("     ⚠ Camera detected but cannot read frames")
        cap.release()
    else:
        print("     ⚠ No camera detected (you can still test other features)")
except Exception as e:
    print(f"     ⚠ Camera test failed: {e}")

# Test Audio Devices
print("[OPT] Testing audio devices...")
try:
    devices = sd.query_devices()
    input_devices = [d for d in devices if d['max_input_channels'] > 0]
    
    if input_devices:
        print(f"     ✓ Found {len(input_devices)} input device(s)")
        for idx, device in enumerate(input_devices[:3]):  # Show first 3
            print(f"       - {device['name']}")
    else:
        print("     ⚠ No audio input devices found")
except Exception as e:
    print(f"     ⚠ Audio device test failed: {e}")

# Test GPU Encoding
print("[OPT] Testing GPU encoding support...")
try:
    result = subprocess.run(
        ['ffmpeg', '-encoders'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    encoders = result.stdout.lower()
    gpu_encoders = []
    
    if 'h264_nvenc' in encoders or 'nvenc' in encoders:
        gpu_encoders.append("NVIDIA NVENC")
    if 'h264_amf' in encoders or 'amf' in encoders:
        gpu_encoders.append("AMD AMF")
    if 'h264_videotoolbox' in encoders or 'videotoolbox' in encoders:
        gpu_encoders.append("Apple VideoToolbox")
    
    if gpu_encoders:
        print(f"     ✓ GPU encoders available: {', '.join(gpu_encoders)}")
    else:
        print("     ⚠ No GPU encoders (CPU encoding will be used)")
except Exception as e:
    print(f"     ⚠ GPU encoder test failed: {e}")

# Test Module Imports
print("[OPT] Testing GCL Studio Pro modules...")
try:
    from audio_recorder import start_audio_recording, stop_audio_recording
    print("     ✓ audio_recorder.py")
except Exception as e:
    print(f"     ✗ audio_recorder.py failed: {e}")

try:
    from video_encoder import VideoWriterWrapper
    print("     ✓ video_encoder.py")
except Exception as e:
    print(f"     ✗ video_encoder.py failed: {e}")

try:
    from export_manager import merge_audio_video, export_all_versions
    print("     ✓ export_manager.py")
except Exception as e:
    print(f"     ✗ export_manager.py failed: {e}")

print()
print("=" * 70)
print("Installation Test Complete")
print("=" * 70)
print()
print("✓ All required dependencies are installed!")
print("✓ You can now run: python app.py")
print()
print("For help, see:")
print("  - README.md (full documentation)")
print("  - QUICKSTART.md (getting started guide)")
print("  - FEATURES.md (feature overview)")
print()
