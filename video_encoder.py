"""
video_encoder.py
GPU-accelerated video encoding detection and configuration
Supports NVENC, AMD AMF, Apple VideoToolbox, and CPU fallback
"""

import platform
import subprocess
import cv2


def detect_gpu_encoder():
    """
    Detect the best available GPU encoder for the current system.
    
    Returns:
        dict: {
            'name': encoder name,
            'fourcc': FourCC code for cv2.VideoWriter,
            'use_ffmpeg': whether to use ffmpeg instead of cv2,
            'ffmpeg_codec': codec name for ffmpeg
        }
    """
    os_type = platform.system()
    
    print(f"[GPU DETECT] Operating System: {os_type}")
    
    # Try to detect GPU using ffmpeg
    try:
        result = subprocess.run(
            ['ffmpeg', '-encoders'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        available_encoders = result.stdout.lower()
        
        # Windows: NVENC (NVIDIA) or AMF (AMD)
        if os_type == "Windows":
            if 'h264_nvenc' in available_encoders or 'nvenc' in available_encoders:
                print("[GPU DETECT] ✓ NVIDIA NVENC detected")
                return {
                    'name': 'NVIDIA NVENC (h264_nvenc)',
                    'fourcc': None,
                    'use_ffmpeg': True,
                    'ffmpeg_codec': 'h264_nvenc'
                }
            elif 'h264_amf' in available_encoders or 'amf' in available_encoders:
                print("[GPU DETECT] ✓ AMD AMF detected")
                return {
                    'name': 'AMD AMF (h264_amf)',
                    'fourcc': None,
                    'use_ffmpeg': True,
                    'ffmpeg_codec': 'h264_amf'
                }
        
        # macOS: VideoToolbox
        elif os_type == "Darwin":
            if 'h264_videotoolbox' in available_encoders or 'videotoolbox' in available_encoders:
                print("[GPU DETECT] ✓ Apple VideoToolbox detected")
                return {
                    'name': 'Apple VideoToolbox (h264_videotoolbox)',
                    'fourcc': None,
                    'use_ffmpeg': True,
                    'ffmpeg_codec': 'h264_videotoolbox'
                }
        
        # Linux: NVENC
        elif os_type == "Linux":
            if 'h264_nvenc' in available_encoders or 'nvenc' in available_encoders:
                print("[GPU DETECT] ✓ NVIDIA NVENC detected")
                return {
                    'name': 'NVIDIA NVENC (h264_nvenc)',
                    'fourcc': None,
                    'use_ffmpeg': True,
                    'ffmpeg_codec': 'h264_nvenc'
                }
    
    except FileNotFoundError:
        print("[GPU DETECT] ffmpeg not found, using CPU encoding")
    except Exception as e:
        print(f"[GPU DETECT] Error detecting GPU: {e}")
    
    # Fallback to CPU encoding
    print("[GPU DETECT] Using CPU encoding (mp4v)")
    return {
        'name': 'CPU (mp4v)',
        'fourcc': cv2.VideoWriter_fourcc(*'mp4v'),
        'use_ffmpeg': False,
        'ffmpeg_codec': None
    }


def create_video_writer_ffmpeg(filename, width, height, fps, codec):
    """
    Create a video writer using ffmpeg pipe for GPU encoding.
    
    Args:
        filename: Output filename
        width: Frame width
        height: Frame height
        fps: Frames per second
        codec: ffmpeg codec name (e.g., 'h264_nvenc')
        
    Returns:
        subprocess.Popen: ffmpeg process for writing frames
    """
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}',
        '-pix_fmt', 'bgr24',
        '-r', str(fps),
        '-i', '-',  # Input from pipe
        '-an',  # No audio
        '-vcodec', codec,
        '-preset', 'fast',
        '-b:v', '5M',  # 5 Mbps bitrate
        filename
    ]
    
    print(f"[FFMPEG WRITER] Starting ffmpeg process: {codec}")
    print(f"[FFMPEG WRITER] Resolution: {width}x{height} @ {fps}fps")
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return process


class VideoWriterWrapper:
    """
    Wrapper class that handles both cv2.VideoWriter and ffmpeg pipe writing.
    """
    
    def __init__(self, filename, width, height, fps=20.0):
        """
        Initialize video writer with automatic GPU detection.
        
        Args:
            filename: Output filename
            width: Frame width
            height: Frame height
            fps: Frames per second
        """
        self.filename = filename
        self.width = width
        self.height = height
        self.fps = fps
        self.encoder_info = detect_gpu_encoder()
        self.writer = None
        self.ffmpeg_process = None
        self.is_opened = False
        
        print(f"[VIDEO WRITER] Encoder: {self.encoder_info['name']}")
        
        if self.encoder_info['use_ffmpeg']:
            # Use ffmpeg for GPU encoding
            try:
                self.ffmpeg_process = create_video_writer_ffmpeg(
                    filename, width, height, fps,
                    self.encoder_info['ffmpeg_codec']
                )
                self.is_opened = True
                print(f"[VIDEO WRITER] ✓ FFmpeg GPU writer initialized")
            except Exception as e:
                print(f"[VIDEO WRITER] ERROR: Failed to initialize ffmpeg: {e}")
                print("[VIDEO WRITER] Falling back to CPU encoding")
                self._init_cpu_writer()
        else:
            # Use cv2.VideoWriter for CPU encoding
            self._init_cpu_writer()
    
    def _init_cpu_writer(self):
        """Initialize CPU-based cv2.VideoWriter."""
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.writer = cv2.VideoWriter(
            self.filename,
            fourcc,
            self.fps,
            (self.width, self.height)
        )
        self.is_opened = self.writer.isOpened()
        
        if self.is_opened:
            print(f"[VIDEO WRITER] ✓ CPU writer initialized (mp4v)")
        else:
            print(f"[VIDEO WRITER] ERROR: Failed to open CPU writer")
    
    def write(self, frame):
        """
        Write a frame to the video.
        
        Args:
            frame: BGR frame (numpy array)
        """
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.write(frame.tobytes())
            except Exception as e:
                print(f"[VIDEO WRITER] ERROR writing to ffmpeg: {e}")
        elif self.writer:
            self.writer.write(frame)
    
    def release(self):
        """Release the video writer and close files."""
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.wait(timeout=10)
                print("[VIDEO WRITER] ✓ FFmpeg process closed")
            except Exception as e:
                print(f"[VIDEO WRITER] ERROR closing ffmpeg: {e}")
        
        if self.writer:
            self.writer.release()
            print("[VIDEO WRITER] ✓ CV2 writer released")
        
        self.is_opened = False
    
    def isOpened(self):
        """Check if writer is opened."""
        return self.is_opened
    
    def get_encoder_name(self):
        """Get the name of the encoder being used."""
        return self.encoder_info['name']
