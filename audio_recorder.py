"""
audio_recorder.py
Professional cross-platform audio recording module for GCL Studio Pro
Supports Windows, macOS, and Linux

Features:
- Multi-track recording (mic + system audio)
- Pause/Resume capability
- Real-time audio level monitoring
- Thread-safe queue-based recording
"""

import sounddevice as sd
import soundfile as sf
import threading
import os
from datetime import datetime
import queue
import numpy as np
import platform

# Global state variables
_recording_thread = None
_system_audio_thread = None
_monitoring_thread = None
_is_recording = False
_is_paused = False
_audio_queue = None
_system_audio_queue = None
_audio_file_mic = None
_audio_file_system = None
_audio_filename_mic = None
_audio_filename_system = None
_current_audio_level = 0.0
_level_callback = None

# Audio monitoring
_monitor_queue = None
_is_monitoring = False


def start_audio_monitoring(level_callback=None):
    """
    Start real-time audio level monitoring.
    
    Args:
        level_callback: Function to call with audio level (0.0 to 1.0+)
    """
    global _monitoring_thread, _is_monitoring, _monitor_queue, _level_callback
    
    if _is_monitoring:
        print("[AUDIO MONITOR] Already monitoring")
        return
    
    _level_callback = level_callback
    _monitor_queue = queue.Queue()
    _is_monitoring = True
    
    _monitoring_thread = threading.Thread(target=_monitor_audio_thread, daemon=True)
    _monitoring_thread.start()
    
    print("[AUDIO MONITOR] ✓ Monitoring started")


def stop_audio_monitoring():
    """Stop audio level monitoring."""
    global _monitoring_thread, _is_monitoring, _monitor_queue, _level_callback
    
    if not _is_monitoring:
        return
    
    _is_monitoring = False
    
    if _monitoring_thread is not None:
        _monitoring_thread.join(timeout=2.0)
    
    _monitor_queue = None
    _level_callback = None
    
    print("[AUDIO MONITOR] ✓ Monitoring stopped")


def get_audio_level():
    """Get current audio level (0.0 to 1.0+)."""
    return _current_audio_level


def _monitor_audio_thread():
    """Background thread for audio level monitoring."""
    global _current_audio_level
    
    sample_rate = 44100
    channels = 2
    blocksize = 2048
    
    def monitor_callback(indata, frames, time_info, status):
        """Callback for audio monitoring."""
        if status:
            print(f"[AUDIO MONITOR] Status: {status}")
        _monitor_queue.put(indata.copy())
    
    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            callback=monitor_callback,
            blocksize=blocksize,
            dtype='float32'
        ):
            while _is_monitoring:
                try:
                    audio_data = _monitor_queue.get(timeout=0.1)
                    
                    # Calculate RMS level
                    rms = np.sqrt(np.mean(audio_data**2))
                    _current_audio_level = float(rms)
                    
                    # Call callback if provided
                    if _level_callback:
                        _level_callback(_current_audio_level)
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[AUDIO MONITOR] ERROR: {e}")
                    break
    
    except Exception as e:
        print(f"[AUDIO MONITOR] ERROR opening stream: {e}")


def start_audio_recording(timestamp=None, record_system_audio=True):
    """
    Start multi-track audio recording in background threads.
    
    Args:
        timestamp: Optional timestamp string (YYYYMMDD_HHMMSS) to sync with video
        record_system_audio: Whether to attempt system audio recording
        
    Returns:
        dict: Dictionary with 'mic' and 'system' file paths
    """
    global _recording_thread, _system_audio_thread, _is_recording, _is_paused
    global _audio_queue, _system_audio_queue, _audio_file_mic, _audio_file_system
    global _audio_filename_mic, _audio_filename_system
    
    if _is_recording:
        print("[AUDIO] Already recording, ignoring start request")
        return {"mic": _audio_filename_mic, "system": _audio_filename_system}
    
    # Create recordings directory if it doesn't exist
    os.makedirs("recordings", exist_ok=True)
    print("[AUDIO] Recordings directory ready")
    
    # Generate filenames with timestamp
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    _audio_filename_mic = f"recordings/audio_mic_{timestamp}.wav"
    _audio_filename_system = None
    
    print(f"[AUDIO] Initializing audio recording: {_audio_filename_mic}")
    print("[AUDIO] Sample rate: 44100 Hz, Channels: 2 (Stereo)")
    
    # Initialize queue for thread-safe audio data transfer
    _audio_queue = queue.Queue()
    
    # Set recording flags
    _is_recording = True
    _is_paused = False
    
    # Start microphone recording thread
    _recording_thread = threading.Thread(target=_record_audio_thread, daemon=True)
    _recording_thread.start()
    
    print(f"[AUDIO] ✓ Microphone recording thread started")
    
    # Attempt system audio recording if requested
    if record_system_audio:
        try:
            _audio_filename_system = f"recordings/audio_system_{timestamp}.wav"
            _system_audio_queue = queue.Queue()
            
            _system_audio_thread = threading.Thread(target=_record_system_audio_thread, daemon=True)
            _system_audio_thread.start()
            
            print(f"[AUDIO] ✓ System audio recording thread started: {_audio_filename_system}")
        except Exception as e:
            print(f"[AUDIO] System audio not available: {e}")
            _audio_filename_system = None
    
    return {"mic": _audio_filename_mic, "system": _audio_filename_system}


def pause_audio_recording():
    """Pause audio recording without closing files."""
    global _is_paused
    
    if not _is_recording:
        print("[AUDIO] Not recording, cannot pause")
        return
    
    if _is_paused:
        print("[AUDIO] Already paused")
        return
    
    _is_paused = True
    print("[AUDIO] ✓ Recording PAUSED")


def resume_audio_recording():
    """Resume paused audio recording."""
    global _is_paused
    
    if not _is_recording:
        print("[AUDIO] Not recording, cannot resume")
        return
    
    if not _is_paused:
        print("[AUDIO] Already recording")
        return
    
    _is_paused = False
    print("[AUDIO] ✓ Recording RESUMED")


def stop_audio_recording():
    """
    Stop the current audio recording and close all files.
    """
    global _recording_thread, _system_audio_thread, _is_recording, _is_paused
    global _audio_queue, _system_audio_queue, _audio_file_mic, _audio_file_system
    global _audio_filename_mic, _audio_filename_system
    
    if not _is_recording:
        print("[AUDIO] Not currently recording, ignoring stop request")
        return
    
    print("[AUDIO] Stopping audio recording...")
    
    # Signal threads to stop
    _is_recording = False
    _is_paused = False
    
    # Wait for threads to finish
    if _recording_thread is not None:
        _recording_thread.join(timeout=5.0)
        print("[AUDIO] ✓ Microphone recording thread stopped")
    
    if _system_audio_thread is not None:
        _system_audio_thread.join(timeout=5.0)
        print("[AUDIO] ✓ System audio recording thread stopped")
    
    # Close audio files if still open
    if _audio_file_mic is not None:
        _audio_file_mic.close()
        _audio_file_mic = None
        print(f"[AUDIO] ✓ Mic audio file closed: {_audio_filename_mic}")
    
    if _audio_file_system is not None:
        _audio_file_system.close()
        _audio_file_system = None
        print(f"[AUDIO] ✓ System audio file closed: {_audio_filename_system}")
    
    print("[AUDIO] ✓ Audio recording stopped successfully")
    
    # Reset state
    _recording_thread = None
    _system_audio_thread = None
    _audio_queue = None
    _system_audio_queue = None
    _audio_filename_mic = None
    _audio_filename_system = None


def _record_audio_thread():
    """
    Internal thread function that handles microphone audio recording.
    Runs in background and writes audio data to file continuously.
    """
    global _audio_file_mic, _is_recording, _is_paused, _audio_queue
    
    sample_rate = 44100
    channels = 2
    blocksize = 4096
    
    print(f"[AUDIO MIC] Thread started with blocksize={blocksize}")
    
    try:
        # Open audio file for writing
        _audio_file_mic = sf.SoundFile(
            _audio_filename_mic,
            mode='w',
            samplerate=sample_rate,
            channels=channels,
            subtype='PCM_16'
        )
        print(f"[AUDIO MIC] ✓ Audio file opened: {_audio_filename_mic}")
        
        frames_written = 0
        
        # Callback function for sounddevice stream
        def audio_callback(indata, frames, time_info, status):
            """Called by sounddevice for each audio block"""
            if status:
                print(f"[AUDIO MIC] Status: {status}")
            
            # Put audio data in queue for processing
            _audio_queue.put(indata.copy())
        
        # Open audio input stream
        print("[AUDIO MIC] Opening audio input stream...")
        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            callback=audio_callback,
            blocksize=blocksize,
            dtype='float32'
        ):
            print("[AUDIO MIC] ✓ Audio input stream opened successfully")
            print("[AUDIO MIC] Recording microphone input...")
            
            # Main recording loop
            while _is_recording:
                try:
                    # Get audio data from queue (timeout to check _is_recording flag)
                    audio_data = _audio_queue.get(timeout=0.1)
                    
                    # Only write if not paused
                    if not _is_paused:
                        _audio_file_mic.write(audio_data)
                        frames_written += len(audio_data)
                        
                        # Log progress every ~2 seconds (44100 * 2 samples)
                        if frames_written % (sample_rate * 2) < blocksize:
                            seconds = frames_written / sample_rate
                            print(f"[AUDIO MIC] Recording... {seconds:.1f}s ({frames_written} frames)")
                    
                except queue.Empty:
                    # No audio data available, continue loop
                    continue
                except Exception as e:
                    print(f"[AUDIO MIC] ERROR writing audio data: {e}")
                    break
            
            print(f"[AUDIO MIC] ✓ Recording loop finished - {frames_written} total frames")
    
    except Exception as e:
        print(f"[AUDIO MIC] ERROR in recording thread: {e}")
        _is_recording = False
    
    finally:
        # Ensure file is closed
        if _audio_file_mic is not None and not _audio_file_mic.closed:
            _audio_file_mic.close()
            print("[AUDIO MIC] Audio file closed in finally block")


def _record_system_audio_thread():
    """
    Internal thread function that handles system audio recording.
    Note: System audio capture is platform-dependent and may not work everywhere.
    """
    global _audio_file_system, _is_recording, _is_paused, _system_audio_queue
    
    sample_rate = 44100
    channels = 2
    blocksize = 4096
    
    print(f"[AUDIO SYSTEM] Thread started with blocksize={blocksize}")
    
    try:
        # Open audio file for writing
        _audio_file_system = sf.SoundFile(
            _audio_filename_system,
            mode='w',
            samplerate=sample_rate,
            channels=channels,
            subtype='PCM_16'
        )
        print(f"[AUDIO SYSTEM] ✓ Audio file opened: {_audio_filename_system}")
        
        frames_written = 0
        
        # Attempt to find loopback/system audio device
        system_device = None
        devices = sd.query_devices()
        
        # Platform-specific device detection
        os_type = platform.system()
        
        for idx, device in enumerate(devices):
            device_name = device['name'].lower()
            
            # Windows: Look for "stereo mix" or "loopback"
            if os_type == "Windows" and ('stereo mix' in device_name or 'loopback' in device_name):
                system_device = idx
                break
            
            # macOS: Look for "BlackHole" or similar virtual devices
            elif os_type == "Darwin" and ('blackhole' in device_name or 'soundflower' in device_name):
                system_device = idx
                break
            
            # Linux: Look for pulse monitor devices
            elif os_type == "Linux" and 'monitor' in device_name:
                system_device = idx
                break
        
        if system_device is None:
            print(f"[AUDIO SYSTEM] No system audio device found on {os_type}")
            print("[AUDIO SYSTEM] Skipping system audio recording")
            return
        
        print(f"[AUDIO SYSTEM] Using device: {devices[system_device]['name']}")
        
        # Callback function for sounddevice stream
        def system_audio_callback(indata, frames, time_info, status):
            """Called by sounddevice for each system audio block"""
            if status:
                print(f"[AUDIO SYSTEM] Status: {status}")
            
            _system_audio_queue.put(indata.copy())
        
        # Open system audio input stream
        with sd.InputStream(
            device=system_device,
            samplerate=sample_rate,
            channels=channels,
            callback=system_audio_callback,
            blocksize=blocksize,
            dtype='float32'
        ):
            print("[AUDIO SYSTEM] ✓ System audio stream opened successfully")
            
            # Main recording loop
            while _is_recording:
                try:
                    audio_data = _system_audio_queue.get(timeout=0.1)
                    
                    # Only write if not paused
                    if not _is_paused:
                        _audio_file_system.write(audio_data)
                        frames_written += len(audio_data)
                        
                        if frames_written % (sample_rate * 2) < blocksize:
                            seconds = frames_written / sample_rate
                            print(f"[AUDIO SYSTEM] Recording... {seconds:.1f}s ({frames_written} frames)")
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[AUDIO SYSTEM] ERROR writing audio data: {e}")
                    break
            
            print(f"[AUDIO SYSTEM] ✓ Recording loop finished - {frames_written} total frames")
    
    except Exception as e:
        print(f"[AUDIO SYSTEM] ERROR in recording thread: {e}")
        print("[AUDIO SYSTEM] System audio recording failed, continuing with mic only")
    
    finally:
        if _audio_file_system is not None and not _audio_file_system.closed:
            _audio_file_system.close()
            print("[AUDIO SYSTEM] Audio file closed in finally block")


# Module test
if __name__ == "__main__":
    print("=" * 70)
    print("Testing audio_recorder.py module")
    print("=" * 70)
    
    import time
    
    # Test recording for 5 seconds
    print("\nStarting 5-second test recording...")
    audio_path = start_audio_recording()
    print(f"Recording to: {audio_path}")
    
    time.sleep(5)
    
    print("\nStopping recording...")
    stop_audio_recording()
    
    print("\n✓ Test complete!")
    print(f"Check file: {audio_path}")
