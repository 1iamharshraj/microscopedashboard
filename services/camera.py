"""
Camera service for Microbe Insights
Handles CSI camera streaming with GStreamer and OpenCV
"""

import cv2
import threading
import time
import numpy as np
from typing import Optional, Tuple, Callable
import logging

logger = logging.getLogger(__name__)

class GStreamerCamera:
    """GStreamer-based camera interface with real-time capture capabilities"""
    
    def __init__(self, 
                 camera_id: int = 0,
                 width: int = 1280,
                 height: int = 720,
                 fps: int = 30,
                 camera_type: str = "usb"):
        """
        Initialize GStreamer camera
        
        Args:
            camera_id: Camera device ID (0 for default camera)
            width: Video width
            height: Video height  
            fps: Frames per second
            camera_type: Type of camera ("usb", "csi", "ip")
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_type = camera_type
        
        self.cap = None
        self.is_streaming = False
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
        # Frame processing callback
        self.frame_callback = None
        
    def _get_gstreamer_pipeline(self) -> str:
        """Generate GStreamer pipeline based on camera type"""
        
        if self.camera_type == "csi":
            # CSI camera pipeline for Jetson Nano
            pipeline = (
                f"nvarguscamerasrc sensor-id={self.camera_id} ! "
                f"video/x-raw(memory:NVMM), width={self.width}, height={self.height}, "
                f"format=NV12, framerate={self.fps}/1 ! "
                f"nvvidconv flip-method=0 ! "
                f"video/x-raw, width={self.width}, height={self.height}, format=BGRx ! "
                f"videoconvert ! video/x-raw, format=BGR ! "
                f"appsink"
            )
        elif self.camera_type == "ip":
            # IP camera pipeline
            pipeline = (
                f"rtspsrc location={self.camera_id} ! "
                f"rtph264depay ! h264parse ! avdec_h264 ! "
                f"videoconvert ! video/x-raw, format=BGR ! "
                f"videoscale ! video/x-raw, width={self.width}, height={self.height} ! "
                f"appsink"
            )
        else:
            # USB camera pipeline
            pipeline = (
                f"v4l2src device=/dev/video{self.camera_id} ! "
                f"video/x-raw, width={self.width}, height={self.height}, "
                f"framerate={self.fps}/1, format=YUY2 ! "
                f"videoconvert ! video/x-raw, format=BGR ! "
                f"appsink"
            )
        
        return pipeline
    
    def _get_opencv_backend(self) -> int:
        """Get OpenCV backend for GStreamer"""
        try:
            # Try GStreamer backend first
            return cv2.CAP_GSTREAMER
        except:
            # Fallback to default backend
            return cv2.CAP_ANY
    
    def start_streaming(self) -> bool:
        """Start camera streaming"""
        try:
            if self.is_streaming:
                logger.warning("Camera is already streaming")
                return True
            
            # Try GStreamer pipeline first
            if self.camera_type in ["csi", "ip"] or self.camera_type == "usb":
                pipeline = self._get_gstreamer_pipeline()
                logger.info(f"Trying GStreamer pipeline: {pipeline}")
                
                self.cap = cv2.VideoCapture(pipeline, self._get_opencv_backend())
                
                if not self.cap.isOpened():
                    logger.warning("GStreamer pipeline failed, trying default backend")
                    self.cap = cv2.VideoCapture(self.camera_id)
            else:
                self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.camera_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size for real-time
            
            self.is_streaming = True
            
            # Start capture thread
            self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
            self.capture_thread.start()
            
            logger.info(f"Camera streaming started: {self.camera_type} camera {self.camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start camera streaming: {e}")
            return False
    
    def stop_streaming(self):
        """Stop camera streaming"""
        self.is_streaming = False
        
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        logger.info("Camera streaming stopped")
    
    def _capture_frames(self):
        """Internal frame capture loop"""
        while self.is_streaming and self.cap:
            try:
                ret, frame = self.cap.read()
                if ret:
                    with self.frame_lock:
                        self.latest_frame = frame.copy()
                    
                    # Call frame processing callback if set
                    if self.frame_callback:
                        try:
                            self.frame_callback(frame)
                        except Exception as e:
                            logger.error(f"Frame callback error: {e}")
                else:
                    logger.warning("Failed to read frame from camera")
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Frame capture error: {e}")
                time.sleep(0.1)
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the latest captured frame"""
        with self.frame_lock:
            return self.latest_frame.copy() if self.latest_frame is not None else None
    
    def set_frame_callback(self, callback: Callable[[np.ndarray], None]):
        """Set callback function for frame processing"""
        self.frame_callback = callback
    
    def capture_snapshot(self) -> Optional[np.ndarray]:
        """Capture a single frame snapshot"""
        if not self.is_streaming:
            return None
        
        frame = self.get_latest_frame()
        if frame is not None:
            logger.info("Snapshot captured")
        
        return frame
    
    def get_camera_info(self) -> dict:
        """Get camera information"""
        info = {
            "camera_id": self.camera_id,
            "camera_type": self.camera_type,
            "resolution": f"{self.width}x{self.height}",
            "fps": self.fps,
            "is_streaming": self.is_streaming,
            "backend": "GStreamer" if self.camera_type in ["csi", "ip"] else "OpenCV"
        }
        
        if self.cap and self.cap.isOpened():
            info["actual_fps"] = self.cap.get(cv2.CAP_PROP_FPS)
            info["actual_width"] = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            info["actual_height"] = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        return info

class CameraManager:
    """Manager for multiple camera instances"""
    
    def __init__(self):
        self.cameras = {}
        self.active_camera_id = None
    
    def add_camera(self, 
                   camera_id: int,
                   camera_type: str = "usb",
                   width: int = 1280,
                   height: int = 720,
                   fps: int = 30) -> bool:
        """Add a new camera"""
        try:
            camera = GStreamerCamera(
                camera_id=camera_id,
                width=width,
                height=height,
                fps=fps,
                camera_type=camera_type
            )
            
            self.cameras[camera_id] = camera
            
            # Set as active if it's the first camera
            if self.active_camera_id is None:
                self.active_camera_id = camera_id
            
            logger.info(f"Camera {camera_id} added ({camera_type})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add camera {camera_id}: {e}")
            return False
    
    def start_camera(self, camera_id: int) -> bool:
        """Start streaming from a specific camera"""
        if camera_id not in self.cameras:
            logger.error(f"Camera {camera_id} not found")
            return False
        
        success = self.cameras[camera_id].start_streaming()
        if success:
            self.active_camera_id = camera_id
        
        return success
    
    def stop_camera(self, camera_id: int):
        """Stop streaming from a specific camera"""
        if camera_id in self.cameras:
            self.cameras[camera_id].stop_streaming()
    
    def stop_all_cameras(self):
        """Stop all cameras"""
        for camera in self.cameras.values():
            camera.stop_streaming()
    
    def get_active_frame(self) -> Optional[np.ndarray]:
        """Get frame from active camera"""
        if self.active_camera_id and self.active_camera_id in self.cameras:
            return self.cameras[self.active_camera_id].get_latest_frame()
        return None
    
    def capture_snapshot(self, camera_id: Optional[int] = None) -> Optional[np.ndarray]:
        """Capture snapshot from specified camera or active camera"""
        if camera_id is None:
            camera_id = self.active_camera_id
        
        if camera_id and camera_id in self.cameras:
            return self.cameras[camera_id].capture_snapshot()
        return None
    
    def get_camera_list(self) -> list:
        """Get list of available cameras"""
        return list(self.cameras.keys())
    
    def get_camera_info(self, camera_id: int) -> Optional[dict]:
        """Get information about a specific camera"""
        if camera_id in self.cameras:
            return self.cameras[camera_id].get_camera_info()
        return None

# Global camera manager instance
camera_manager = CameraManager()
