import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
import os
from datetime import datetime
import threading
from audio_recorder import (
    start_audio_recording, stop_audio_recording,
    pause_audio_recording, resume_audio_recording,
    start_audio_monitoring, stop_audio_monitoring,
    get_audio_level
)
from video_encoder import VideoWriterWrapper
from export_manager import merge_audio_video, export_all_versions

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create main app window
app = ctk.CTk()
app.title("GCL Studio Pro")
app.geometry("500x300")


def open_new_window():
    new_window = ctk.CTkToplevel(app)
    new_window.title("Session Window")
    new_window.geometry("400x200")

    msg = ctk.CTkLabel(new_window, text="Welcome to your Session!", font=("Arial", 20))
    msg.pack(pady=40)


def open_creator_studio():
    studio = ctk.CTkToplevel(app)
    studio.title("GCL Studio Pro - Creator Studio")
    studio.geometry("1000x700")

    # Recording state variables
    recording_state = "idle"  # idle, recording, paused, stopped
    video_writer = None
    current_frame = None
    frame_count = 0
    video_filename = None
    audio_filenames = None
    encoder_name = "Detecting..."
    export_results = None

    # Buttons frame
    button_frame = ctk.CTkFrame(studio)
    button_frame.pack(pady=12)

    # Status frame
    status_frame = ctk.CTkFrame(studio)
    status_frame.pack(pady=5, fill="x", padx=12)

    # GPU encoder label
    gpu_label = ctk.CTkLabel(status_frame, text=f"Encoder: {encoder_name}", font=("Arial", 12))
    gpu_label.pack(side="left", padx=10)

    # Recording state label
    state_label = ctk.CTkLabel(status_frame, text="● IDLE", font=("Arial", 14, "bold"), text_color="gray")
    state_label.pack(side="left", padx=10)

    # Audio level frame
    audio_frame = ctk.CTkFrame(studio)
    audio_frame.pack(pady=5, fill="x", padx=12)

    audio_label = ctk.CTkLabel(audio_frame, text="Audio Level:", font=("Arial", 12))
    audio_label.pack(side="left", padx=5)

    # Audio level meter using progressbar
    audio_meter = ctk.CTkProgressBar(audio_frame, width=300, height=20)
    audio_meter.pack(side="left", padx=10)
    audio_meter.set(0)

    audio_level_text = ctk.CTkLabel(audio_frame, text="0%", font=("Arial", 12))
    audio_level_text.pack(side="left", padx=5)

    # Export results frame
    export_frame = ctk.CTkFrame(studio)
    export_frame.pack(pady=5, fill="x", padx=12)

    export_label = ctk.CTkLabel(export_frame, text="", font=("Arial", 10), wraplength=900)
    export_label.pack(pady=5)

    def update_state_label(state):
        """Update the recording state label with color coding."""
        nonlocal recording_state
        recording_state = state
        
        if state == "idle":
            state_label.configure(text="● IDLE", text_color="gray")
        elif state == "recording":
            state_label.configure(text="● RECORDING", text_color="red")
        elif state == "paused":
            state_label.configure(text="● PAUSED", text_color="yellow")
        elif state == "stopped":
            state_label.configure(text="● STOPPED", text_color="green")

    def update_audio_level(level):
        """Update audio level meter (called from audio monitoring thread)."""
        try:
            # Normalize level (0.0 to 1.0+, clamp at 1.5 for display)
            normalized = min(level * 10, 1.0)  # Amplify for visibility
            
            audio_meter.set(normalized)
            
            percent = int(normalized * 100)
            audio_level_text.configure(text=f"{percent}%")
            
            # Color coding
            if level > 0.8:  # Clipping warning
                audio_meter.configure(progress_color="red")
            elif level > 0.6:  # Close to clipping
                audio_meter.configure(progress_color="yellow")
            else:  # Normal
                audio_meter.configure(progress_color="green")
        
        except Exception as e:
            pass  # Ignore threading errors

    def start_recording():
        nonlocal video_writer, frame_count, video_filename, audio_filenames, encoder_name
        
        if recording_state != "idle":
            print("[VIDEO] Cannot start recording: not in idle state")
            return
        
        if current_frame is None:
            print("[VIDEO] Cannot start recording: no frame available")
            return
        
        print("[RECORDING] ========== Starting Recording Session ==========")
        update_state_label("recording")
        
        # Create recordings directory if it doesn't exist
        os.makedirs("recordings", exist_ok=True)
        
        # Generate SHARED timestamp for video and audio sync
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"recordings/video_{timestamp}.mp4"
        
        print(f"[VIDEO] Timestamp: {timestamp}")
        print(f"[VIDEO] Output file: {video_filename}")
        
        # Get frame dimensions
        height, width = current_frame.shape[:2]
        print(f"[VIDEO] Frame dimensions: {width}x{height}")
        
        # Initialize VideoWriter with GPU detection
        video_writer = VideoWriterWrapper(video_filename, width, height, fps=20.0)
        
        if not video_writer.isOpened():
            print(f"[VIDEO] ERROR: Failed to open VideoWriter")
            video_writer = None
            update_state_label("idle")
            return
        
        encoder_name = video_writer.get_encoder_name()
        gpu_label.configure(text=f"Encoder: {encoder_name}")
        print(f"[VIDEO] ✓ VideoWriter initialized with {encoder_name}")
        
        # Start audio recording with SAME timestamp (mic + system if available)
        audio_filenames = start_audio_recording(timestamp, record_system_audio=True)
        print(f"[SYNC] ✓ Audio started")
        print(f"[SYNC]   Mic: {audio_filenames.get('mic')}")
        if audio_filenames.get('system'):
            print(f"[SYNC]   System: {audio_filenames.get('system')}")
        
        # Set recording state
        frame_count = 0
        
        # Update button states
        record_btn.configure(state="disabled")
        pause_btn.configure(state="normal")
        resume_btn.configure(state="disabled")
        stop_btn.configure(state="normal")
        
        print("[RECORDING] ✓ Recording session started successfully")
        print("[RECORDING] ========================================")

    def pause_recording():
        if recording_state != "recording":
            print("[RECORDING] Cannot pause: not in recording state")
            return
        
        print("[RECORDING] ========== Pausing Recording ==========")
        update_state_label("paused")
        
        # Pause audio
        pause_audio_recording()
        
        # Update button states
        pause_btn.configure(state="disabled")
        resume_btn.configure(state="normal")
        
        print("[RECORDING] ✓ Recording paused")

    def resume_recording():
        if recording_state != "paused":
            print("[RECORDING] Cannot resume: not in paused state")
            return
        
        print("[RECORDING] ========== Resuming Recording ==========")
        update_state_label("recording")
        
        # Resume audio
        resume_audio_recording()
        
        # Update button states
        pause_btn.configure(state="normal")
        resume_btn.configure(state="disabled")
        
        print("[RECORDING] ✓ Recording resumed")

    def stop_recording():
        nonlocal video_writer, frame_count, video_filename, audio_filenames, export_results
        
        if recording_state not in ["recording", "paused"]:
            print("[VIDEO] Cannot stop recording: not currently recording")
            return
        
        print("[RECORDING] ========== Stopping Recording Session ==========")
        update_state_label("stopped")
        
        # Stop audio recording first
        print("[SYNC] Stopping audio...")
        stop_audio_recording()
        print("[SYNC] ✓ Audio stopped")
        
        # Stop video recording
        print("[VIDEO] Stopping video...")
        video_writer.release()
        print(f"[VIDEO] ✓ Recording stopped - {frame_count} frames written")
        
        # Store filenames before resetting
        saved_video = video_filename
        saved_audio = audio_filenames
        
        # Reset state
        video_writer = None
        frame_count = 0
        
        # Update button states
        record_btn.configure(state="normal")
        pause_btn.configure(state="disabled")
        resume_btn.configure(state="disabled")
        stop_btn.configure(state="disabled")
        
        print("[RECORDING] ✓ All recordings stopped")
        
        # Merge audio and video in a background thread to avoid blocking GUI
        def merge_and_export():
            nonlocal export_results
            
            print("[RECORDING] Starting merge and export process...")
            
            # Merge video with audio(s)
            merged_path = merge_audio_video(saved_video, saved_audio)
            
            if merged_path:
                print(f"[FINAL] ✓ Merged video completed: {merged_path}")
                
                # Export for platforms
                export_results = export_all_versions(merged_path)
                
                # Update GUI with results
                result_text = f"✓ Original: {export_results['original']}\n"
                if export_results['tiktok']:
                    result_text += f"✓ TikTok: {export_results['tiktok']}\n"
                if export_results['youtube']:
                    result_text += f"✓ YouTube: {export_results['youtube']}"
                
                export_label.configure(text=result_text)
                
                print("[FINAL] ✓ All exports completed!")
            else:
                print("[FINAL] WARNING: Merge failed, separate files saved")
                export_label.configure(text=f"⚠ Merge failed. Files saved:\nVideo: {saved_video}\nAudio: {saved_audio.get('mic')}")
        
        # Run merge in background thread
        merge_thread = threading.Thread(target=merge_and_export, daemon=True)
        merge_thread.start()
        
        # Reset filenames
        video_filename = None
        audio_filenames = None
        
        print("[RECORDING] ========================================")
        
        # Return to idle after a delay
        studio.after(1000, lambda: update_state_label("idle"))

    # Control buttons
    record_btn = ctk.CTkButton(
        button_frame, 
        text="⬤ Start Recording", 
        command=start_recording,
        fg_color="red",
        hover_color="darkred",
        width=150
    )
    record_btn.grid(row=0, column=0, padx=5)

    pause_btn = ctk.CTkButton(
        button_frame,
        text="⏸ Pause",
        command=pause_recording,
        state="disabled",
        width=120
    )
    pause_btn.grid(row=0, column=1, padx=5)

    resume_btn = ctk.CTkButton(
        button_frame,
        text="▶ Resume",
        command=resume_recording,
        state="disabled",
        width=120
    )
    resume_btn.grid(row=0, column=2, padx=5)

    stop_btn = ctk.CTkButton(
        button_frame,
        text="⬛ Stop",
        command=stop_recording,
        state="disabled",
        fg_color="darkgray",
        hover_color="gray",
        width=120
    )
    stop_btn.grid(row=0, column=3, padx=5)

    # Camera preview area
    preview_frame = ctk.CTkFrame(studio)
    preview_frame.pack(padx=12, pady=12, fill="both", expand=True)

    camera_label = ctk.CTkLabel(preview_frame, text="")
    camera_label.pack(expand=True)

    cap = cv2.VideoCapture(0)

    # Start audio monitoring for level meter
    start_audio_monitoring(level_callback=update_audio_level)

    def update_camera():
        nonlocal current_frame, frame_count
        
        if not cap or not cap.isOpened():
            return
        
        ret, frame = cap.read()
        
        if ret:
            # Store current frame (original BGR format)
            current_frame = frame.copy()
            
            # Write frame to video file if recording (not paused)
            if recording_state == "recording" and video_writer is not None:
                video_writer.write(current_frame)
                frame_count += 1
                
                if frame_count % 20 == 0:  # Log every 20 frames (1 second)
                    print(f"  [VIDEO] Writing frame {frame_count}...")
            
            # Display frame (convert to RGB for display)
            display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(display_frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
        
        camera_label.after(30, update_camera)

    def on_close():
        nonlocal video_writer, video_filename, audio_filenames
        
        print("[STUDIO] Closing Content Creator Studio...")
        
        try:
            # Stop audio monitoring
            stop_audio_monitoring()
            
            if recording_state in ["recording", "paused"] and video_writer:
                print("[STUDIO] Recording in progress, stopping...")
                
                # Stop audio
                print("[STUDIO] Stopping audio...")
                stop_audio_recording()
                
                # Stop video
                print("[STUDIO] Releasing VideoWriter...")
                video_writer.release()
                print(f"[STUDIO] ✓ Final video saved - {frame_count} total frames")
                
                # Merge if both files exist
                if audio_filenames and video_filename:
                    print("[STUDIO] Attempting to merge before close...")
                    merged = merge_audio_video(video_filename, audio_filenames)
                    if merged:
                        print(f"[STUDIO] ✓ Merged on close: {merged}")
            
            if cap and cap.isOpened():
                print("[STUDIO] Releasing camera...")
                cap.release()
                
        except Exception as e:
            print(f"[STUDIO] ERROR during cleanup: {e}")
        
        studio.destroy()
        print("[STUDIO] ✓ Studio closed")

    studio.protocol("WM_DELETE_WINDOW", on_close)
    update_camera()


# Title label
title = ctk.CTkLabel(app, text="GCL Studio Pro", font=("Arial", 28))
title.pack(pady=30)

# Start Session button
button = ctk.CTkButton(app, text="Start Session", command=open_new_window)
button.pack(pady=20)

# Content Creator Studio button
creator_btn = ctk.CTkButton(app, text="Content Creator Studio", command=open_creator_studio)
creator_btn.pack(pady=10)

app.mainloop()
