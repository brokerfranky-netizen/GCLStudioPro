"""
list_devices.py
List all available audio and video devices for GCL Studio Pro

This script helps users identify available recording devices on their system.
"""

import platform

print("=" * 70)
print("GCL Studio Pro - Device List")
print("=" * 70)
print(f"Platform: {platform.system()} {platform.release()}")
print()

# Audio Devices
print("-" * 70)
print("AUDIO DEVICES")
print("-" * 70)
print()

try:
    import sounddevice as sd
    
    devices = sd.query_devices()
    
    # Input devices (microphones)
    input_devices = [(idx, d) for idx, d in enumerate(devices) if d['max_input_channels'] > 0]
    
    if input_devices:
        print(f"Input Devices ({len(input_devices)} found):")
        for idx, device in input_devices:
            channels = device['max_input_channels']
            samplerate = int(device.get('default_samplerate', 0))
            print(f"  [{idx}] {device['name']}")
            print(f"       Channels: {channels}, Sample Rate: {samplerate} Hz")
    else:
        print("No audio input devices found.")
    
    print()
    
    # Output devices (speakers)
    output_devices = [(idx, d) for idx, d in enumerate(devices) if d['max_output_channels'] > 0]
    
    if output_devices:
        print(f"Output Devices ({len(output_devices)} found):")
        for idx, device in output_devices:
            channels = device['max_output_channels']
            samplerate = int(device.get('default_samplerate', 0))
            print(f"  [{idx}] {device['name']}")
            print(f"       Channels: {channels}, Sample Rate: {samplerate} Hz")
    else:
        print("No audio output devices found.")
    
    print()
    
    # Default devices
    try:
        default_input = sd.query_devices(kind='input')
        print(f"Default Input: {default_input['name']}")
    except Exception:
        print("Default Input: Not available")
    
    try:
        default_output = sd.query_devices(kind='output')
        print(f"Default Output: {default_output['name']}")
    except Exception:
        print("Default Output: Not available")

except ImportError:
    print("ERROR: sounddevice module not installed")
    print("Run: pip install sounddevice")
except Exception as e:
    print(f"ERROR listing audio devices: {e}")

print()

# Video Devices
print("-" * 70)
print("VIDEO DEVICES (Cameras)")
print("-" * 70)
print()

try:
    import os
    # Suppress OpenCV warnings for cleaner output (must be set before import)
    os.environ["OPENCV_LOG_LEVEL"] = "SILENT"
    
    import cv2
    
    camera_count = 0
    max_cameras_to_check = 10
    
    print(f"Scanning for cameras (checking indices 0-{max_cameras_to_check - 1})...")
    print()
    
    for i in range(max_cameras_to_check):
        cap = cv2.VideoCapture(i)
        try:
            if cap.isOpened():
                # Read a frame to verify camera is actually working
                ret, frame = cap.read()
                if ret:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    backend = cap.getBackendName()
                    
                    print(f"  [{i}] Camera {camera_count}")
                    print(f"       Resolution: {width}x{height}")
                    print(f"       FPS: {fps:.1f}")
                    print(f"       Backend: {backend}")
                    
                    camera_count += 1
        finally:
            cap.release()
    
    if camera_count == 0:
        print("  No cameras detected.")
    else:
        print()
        print(f"Total cameras found: {camera_count}")

except ImportError:
    print("ERROR: opencv-python module not installed")
    print("Run: pip install opencv-python")
except Exception as e:
    print(f"ERROR listing video devices: {e}")

print()
print("=" * 70)
print("Device scan complete.")
print("=" * 70)
