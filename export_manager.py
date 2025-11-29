"""
export_manager.py
Auto-export functionality for TikTok, YouTube, and platform-optimized videos
"""

import subprocess
import os


def merge_audio_video(video_path, audio_paths, output_path=None):
    """
    Merge video with one or more audio tracks using ffmpeg.
    
    Args:
        video_path: Path to video file (.mp4)
        audio_paths: Dictionary with 'mic' and optionally 'system' audio paths
        output_path: Optional custom output path
        
    Returns:
        str: Path to merged output file, or None on failure
    """
    print(f"[MERGE] Starting merge process...")
    print(f"[MERGE]   Video: {video_path}")
    
    if output_path is None:
        output_path = video_path.replace(".mp4", "_FINAL.mp4")
    
    # Build audio inputs
    mic_audio = audio_paths.get('mic')
    system_audio = audio_paths.get('system')
    
    if not mic_audio:
        print("[MERGE] ERROR: No microphone audio provided")
        return None
    
    print(f"[MERGE]   Mic Audio: {mic_audio}")
    
    # Check if files exist
    if not os.path.exists(video_path):
        print(f"[MERGE] ERROR: Video file not found: {video_path}")
        return None
    
    if not os.path.exists(mic_audio):
        print(f"[MERGE] ERROR: Mic audio file not found: {mic_audio}")
        return None
    
    # Build ffmpeg command
    if system_audio and os.path.exists(system_audio):
        # Merge both mic and system audio
        print(f"[MERGE]   System Audio: {system_audio}")
        
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", mic_audio,
            "-i", system_audio,
            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=longest:normalize=0[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path
        ]
    else:
        # Merge only mic audio
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", mic_audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print(f"[MERGE] ✓ Final merged file created: {output_path}")
            return output_path
        else:
            print(f"[MERGE] ERROR: ffmpeg returned code {result.returncode}")
            print(f"[MERGE] stderr: {result.stderr[:500]}")  # First 500 chars
            return None
    
    except FileNotFoundError:
        print("[MERGE] ERROR: ffmpeg not found. Please install ffmpeg.")
        return None
    except subprocess.TimeoutExpired:
        print("[MERGE] ERROR: Merge process timed out")
        return None
    except Exception as e:
        print(f"[MERGE] ERROR during merge: {e}")
        return None


def export_for_tiktok(input_video, output_path=None):
    """
    Export video optimized for TikTok (vertical 1080x1920).
    
    Args:
        input_video: Path to input video file
        output_path: Optional custom output path
        
    Returns:
        str: Path to TikTok-optimized video, or None on failure
    """
    if output_path is None:
        output_path = input_video.replace(".mp4", "_TIKTOK.mp4")
    
    print(f"[TIKTOK EXPORT] Creating TikTok version...")
    print(f"[TIKTOK EXPORT]   Input: {input_video}")
    print(f"[TIKTOK EXPORT]   Output: {output_path}")
    print(f"[TIKTOK EXPORT]   Resolution: 1080x1920 (vertical)")
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-b:v", "3M",
        "-maxrate", "3M",
        "-bufsize", "6M",
        "-c:a", "aac",
        "-b:a", "128k",
        "-ar", "44100",
        "-movflags", "+faststart",
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            print(f"[TIKTOK EXPORT] ✓ TikTok version created: {output_path}")
            return output_path
        else:
            print(f"[TIKTOK EXPORT] ERROR: ffmpeg returned code {result.returncode}")
            return None
    
    except Exception as e:
        print(f"[TIKTOK EXPORT] ERROR: {e}")
        return None


def export_for_youtube(input_video, output_path=None):
    """
    Export video optimized for YouTube (1920x1080 HD).
    
    Args:
        input_video: Path to input video file
        output_path: Optional custom output path
        
    Returns:
        str: Path to YouTube-optimized video, or None on failure
    """
    if output_path is None:
        output_path = input_video.replace(".mp4", "_YOUTUBE.mp4")
    
    print(f"[YOUTUBE EXPORT] Creating YouTube HD version...")
    print(f"[YOUTUBE EXPORT]   Input: {input_video}")
    print(f"[YOUTUBE EXPORT]   Output: {output_path}")
    print(f"[YOUTUBE EXPORT]   Resolution: 1920x1080 (HD)")
    
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "21",
        "-b:v", "8M",
        "-maxrate", "8M",
        "-bufsize", "16M",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            print(f"[YOUTUBE EXPORT] ✓ YouTube HD version created: {output_path}")
            return output_path
        else:
            print(f"[YOUTUBE EXPORT] ERROR: ffmpeg returned code {result.returncode}")
            return None
    
    except Exception as e:
        print(f"[YOUTUBE EXPORT] ERROR: {e}")
        return None


def export_all_versions(merged_video):
    """
    Export all platform-optimized versions (TikTok + YouTube).
    
    Args:
        merged_video: Path to the merged video file
        
    Returns:
        dict: Dictionary with paths to all exported versions
    """
    results = {
        'original': merged_video,
        'tiktok': None,
        'youtube': None
    }
    
    print("[EXPORT ALL] ========== Creating Platform Exports ==========")
    
    # Export for TikTok
    results['tiktok'] = export_for_tiktok(merged_video)
    
    # Export for YouTube
    results['youtube'] = export_for_youtube(merged_video)
    
    print("[EXPORT ALL] ========================================")
    
    # Summary
    print(f"[EXPORT ALL] Original: {results['original']}")
    if results['tiktok']:
        print(f"[EXPORT ALL] ✓ TikTok: {results['tiktok']}")
    else:
        print(f"[EXPORT ALL] ✗ TikTok export failed")
    
    if results['youtube']:
        print(f"[EXPORT ALL] ✓ YouTube: {results['youtube']}")
    else:
        print(f"[EXPORT ALL] ✗ YouTube export failed")
    
    return results
