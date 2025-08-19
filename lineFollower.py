"""
Line Following Module for FALCON Robot

This module implements computer vision-based line detection and following
using OpenCV. It processes camera frames to detect lines and finish circles
for autonomous navigation.

Author: Inelectronics Student Club
Robot: FALCON
Competition: League of Robotics 2nd Edition
"""

import time
import numpy as np
import cv2
from threading import Thread


class line_follow(Thread):
    """
    Line following thread that processes camera frames to detect
    line position and finish circles.
    """
    
    def __init__(self):
        """Initialize line following parameters."""
        self.cx = None           # Line center X coordinate
        self.cy = None           # Line center Y coordinate  
        self.no_line = False     # Flag for no line detected
        self.frame = None        # Current camera frame
        self.on = False          # Thread running flag
        self.circle = False      # Finish circle detected flag
        self.cropped_image = None # Processed image region
        super().__init__()

    def start(self):
        """Start the line following thread."""
        Thread(target=self.run, args=()).start()
        return self

    def run(self):
        """Main processing loop for line detection."""
        self.on = True
        while self.on:
            try:
                if self.frame is not None:
                    self._process_frame()
                time.sleep(0.01)  # Small delay to prevent CPU overload
            except Exception as e:
                print(f"Line detection error: {e}")

    def _process_frame(self):
        """Process current frame for line and circle detection."""
        try:
            # Crop image to focus on line detection area
            self.cropped_image = self.frame[120:240, 0:320]
            
            # Convert to grayscale for processing
            gray = cv2.cvtColor(self.cropped_image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Threshold to create binary image (line detection)
            _, thresh = cv2.threshold(blur, 24, 255, cv2.THRESH_BINARY_INV)
            
            # Morphological operations to clean up detection
            mask = cv2.erode(thresh, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)
            
            # Find contours for line detection
            contours, _ = cv2.findContours(mask.copy(), 1, cv2.CHAIN_APPROX_NONE)
            
            # Detect finish circle
            self._detect_finish_circle(gray)
            
            # Process line contours
            self._process_line_contours(contours)
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            self.no_line = True

    def _detect_finish_circle(self, gray):
        """
        Detect finish circle in the image.
        
        Args:
            gray: Grayscale image
        """
        circles = cv2.HoughCircles(
            gray, 
            cv2.HOUGH_GRADIENT, 
            1, 100, 
            param1=50, 
            param2=30, 
            minRadius=50, 
            maxRadius=70
        )
        
        self.circle = circles is not None

    def _process_line_contours(self, contours):
        """
        Process detected contours to find line center.
        
        Args:
            contours: List of detected contours
        """
        if len(contours) > 0:
            # Find the largest contour (assumed to be the line)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate moments to find centroid
            moments = cv2.moments(largest_contour)
            
            if moments['m00'] != 0:
                self.cx = int(moments['m10'] / moments['m00'])
                self.cy = int(moments['m01'] / moments['m00'])
                self.no_line = False
            else:
                self.no_line = True
                self.cx = None
        else:
            self.no_line = True
            self.cx = None

    def stop(self):
        """Stop the line following thread."""
        self.on = False

# ============================================================================
# TESTING MODULE
# ============================================================================

if __name__ == '__main__':
    """Test the line following functionality independently."""
    print("Line Following Test Module")
    
    try:
        # Setup camera
        webcam = cv2.VideoCapture(0)
        webcam.set(3, 320)  # Width
        webcam.set(4, 240)  # Height
        webcam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        webcam.set(cv2.CAP_PROP_AUTO_WB, 0)
        
        # Initialize line following
        _, initial_frame = webcam.read()
        line_thread = line_follow()
        line_thread.frame = initial_frame
        line_thread.start()
        
        print("Line following test started. Press 'q' to quit.")
        time.sleep(1)
        
        while True:
            _, frame = webcam.read()
            line_thread.frame = frame
            
            # Display results
            print(f"Line center: {line_thread.cx}, No line: {line_thread.no_line}, Circle: {line_thread.circle}")
            
            # Show processed image if available
            if line_thread.cropped_image is not None:
                cv2.imshow("Line Detection", line_thread.cropped_image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Test interrupted by user")
    finally:
        if 'line_thread' in locals():
            line_thread.stop()
        if 'webcam' in locals():
            webcam.release()
        cv2.destroyAllWindows()
        print("Line following test complete")
