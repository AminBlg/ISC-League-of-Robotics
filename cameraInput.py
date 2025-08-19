"""
Camera Input Module for FALCON Robot

This module provides threaded camera input functionality for real-time
frame capture and processing. It manages camera initialization, frame
capture, and resource cleanup.

Author: Inelectronics Student Club
Robot: FALCON  
Competition: League of Robotics 2nd Edition
"""

import cv2
from threading import Thread
from time import sleep


class camera(Thread):
    """
    Camera thread for continuous frame capture.
    
    Manages camera initialization, frame capture loop, and cleanup.
    Provides frames to other processing threads for computer vision tasks.
    """
    
    def __init__(self, camera_id=0, width=160, height=120):
        """
        Initialize camera thread with specified parameters.
        
        Args:
            camera_id (int): Camera device ID (default: 0)
            width (int): Frame width in pixels (default: 160)
            height (int): Frame height in pixels (default: 120)
        """
        self.frame = None
        self.webcam = cv2.VideoCapture(camera_id)
        self.on = False
        self.width = width
        self.height = height
        super().__init__()

    def start(self):
        """Start the camera capture thread."""
        Thread(target=self.run, args=()).start()
        return self

    def run(self):
        """Main camera capture loop."""
        self.on = True
        
        # Configure camera settings
        self._configure_camera()
        
        print(f"Camera started - Resolution: {self.width}x{self.height}")
        
        while self.on:
            try:
                ret, frame = self.webcam.read()
                if ret:
                    self.frame = frame
                else:
                    print("Warning: Failed to capture frame")
                    
            except Exception as e:
                print(f"Camera capture error: {e}")
                break

    def _configure_camera(self):
        """Configure camera settings for optimal performance."""
        self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.webcam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # Disable auto exposure
        self.webcam.set(cv2.CAP_PROP_AUTO_WB, 0)        # Disable auto white balance
        
        # Optional: Set manual exposure for consistent lighting
        # self.webcam.set(cv2.CAP_PROP_EXPOSURE, -6)

    def stop(self):
        """Stop camera capture and cleanup resources."""
        self.on = False
        if self.webcam.isOpened():
            self.webcam.release()
        cv2.destroyAllWindows()
        print("Camera stopped and resources cleaned up")

    def get_frame(self):
        """
        Get the latest captured frame.
        
        Returns:
            numpy.ndarray: Latest camera frame, or None if no frame available
        """
        return self.frame

    def is_running(self):
        """
        Check if camera thread is running.
        
        Returns:
            bool: True if camera is actively capturing frames
        """
        return self.on


# ============================================================================
# TESTING MODULE
# ============================================================================

if __name__ == "__main__":
    """Test camera functionality independently."""
    print("Camera Test Module")
    
    try:
        # Initialize camera
        camera_thread = camera()
        camera_thread.start()
        
        print("Camera test started. Press 'q' to quit.")
        sleep(2)  # Wait for camera to initialize
        
        while True:
            if camera_thread.frame is not None:
                cv2.imshow("Camera Test", camera_thread.frame)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Test interrupted by user")
    finally:
        if 'camera_thread' in locals():
            camera_thread.stop()
        print("Camera test complete")

