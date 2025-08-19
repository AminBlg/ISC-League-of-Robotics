"""
Color Detection Module for FALCON Robot

This module implements HSV-based color detection for identifying task zones
(Red, Green, Blue) in the competition arena. It processes camera frames to
detect dominant colors in specified regions.

Author: Inelectronics Student Club
Robot: FALCON
Competition: League of Robotics 2nd Edition
"""

from threading import Thread
import numpy as np
import cv2
import time


class scanColor(Thread):
    """
    Color detection thread that analyzes camera frames to identify
    specific colors (Red, Green, Blue) for task zone recognition.
    """
    
    def __init__(self, detection_region=(0.0, 0, 0.2, 0.2)):
        """
        Initialize color detection with configurable parameters.
        
        Args:
            detection_region (tuple): (x1, y1, x2, y2) as fractions of frame size
                                    Default analyzes top-left 20% of frame
        """
        self.color = None           # Detected color ('R', 'G', 'B', or None)
        self.frame = None           # Current camera frame
        self.on = False            # Thread running flag
        self.avg_color = None      # Average HSV color in detection region
        self.cropped_image = None  # Processed image region
        self.detection_region = detection_region
        super().__init__()
        
        # HSV color ranges for detection (calibrated for competition lighting)
        self._init_color_ranges()

    def _init_color_ranges(self):
        """Initialize HSV color ranges for detection."""
        # Red color range (split due to HSV wraparound)
        self.red_lower1 = np.array([0, 87, 111], np.uint8)
        self.red_upper1 = np.array([25, 255, 255], np.uint8)
        self.red_lower2 = np.array([160, 87, 111], np.uint8) 
        self.red_upper2 = np.array([180, 255, 255], np.uint8)
        
        # Green color range
        self.green_lower = np.array([40, 52, 72], np.uint8)
        self.green_upper = np.array([92, 255, 255], np.uint8)
        
        # Blue color range
        self.blue_lower = np.array([94, 70, 82], np.uint8)
        self.blue_upper = np.array([121, 255, 255], np.uint8)

    def start(self):
        """Start the color detection thread."""
        Thread(target=self.run, args=()).start()
        return self

    def run(self):
        """Main color detection processing loop."""
        self.on = True
        while self.on:
            # Small delay to reduce CPU load
            time.sleep(0.1)
            
            try:
                if self.frame is not None:
                    self._process_frame()
            except Exception as e:
                print(f"Color detection error: {e}")

    def _process_frame(self):
        """Process current frame for color detection."""
        try:
            # Extract detection region from frame
            frame_height, frame_width = self.frame.shape[:2]
            x1 = int(frame_width * self.detection_region[0])
            y1 = int(frame_height * self.detection_region[1])
            x2 = int(frame_width * self.detection_region[2])
            y2 = int(frame_height * self.detection_region[3])
            
            # Crop image to detection region
            cropped_frame = self.frame[y1:y2, x1:x2]
            self.cropped_image = cropped_frame
            
            # Convert to HSV color space
            hsv_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)
            
            # Calculate average color in region
            self.avg_color = self._calculate_average_color(hsv_frame)
            
            # Detect dominant color
            self.color = self._classify_color(self.avg_color)
            
        except Exception as e:
            print(f"Frame processing error: {e}")
            self.color = None

    def _calculate_average_color(self, hsv_frame):
        """
        Calculate the average HSV color in the frame.
        
        Args:
            hsv_frame: HSV color space image
            
        Returns:
            numpy.ndarray: Average HSV values [H, S, V]
        """
        avg_color_per_row = np.average(hsv_frame, axis=0)
        avg_color = np.average(avg_color_per_row, axis=0)
        return avg_color

    def _classify_color(self, avg_color):
        """
        Classify the average color into Red, Green, Blue, or None.
        
        Args:
            avg_color: Average HSV color values
            
        Returns:
            str: Detected color ('R', 'G', 'B') or None if no match
        """
        if avg_color is None:
            return None
            
        # Check if color falls within red ranges
        red_match1 = (np.less_equal(avg_color, self.red_upper1).all() and 
                      np.greater_equal(avg_color, self.red_lower1).all())
        red_match2 = (np.less_equal(avg_color, self.red_upper2).all() and 
                      np.greater_equal(avg_color, self.red_lower2).all())
        
        if red_match1 or red_match2:
            return 'R'
            
        # Check for green
        elif (np.less_equal(avg_color, self.green_upper).all() and 
              np.greater_equal(avg_color, self.green_lower).all()):
            return 'G'
            
        # Check for blue
        elif (np.less_equal(avg_color, self.blue_upper).all() and 
              np.greater_equal(avg_color, self.blue_lower).all()):
            return 'B'
            
        return None

    def update_color_ranges(self, color, lower, upper):
        """
        Update color detection ranges for calibration.
        
        Args:
            color (str): Color to update ('R', 'G', 'B')
            lower (list): Lower HSV threshold
            upper (list): Upper HSV threshold
        """
        if color == 'R':
            self.red_lower1 = np.array(lower, np.uint8)
            self.red_upper1 = np.array(upper, np.uint8)
        elif color == 'G':
            self.green_lower = np.array(lower, np.uint8)
            self.green_upper = np.array(upper, np.uint8)
        elif color == 'B':
            self.blue_lower = np.array(lower, np.uint8)
            self.blue_upper = np.array(upper, np.uint8)

    def stop(self):
        """Stop the color detection thread."""
        self.on = False


# ============================================================================
# TESTING MODULE
# ============================================================================

if __name__ == '__main__':
    """Test color detection functionality independently."""
    print("Color Detection Test Module")
    
    try:
        # Setup camera
        webcam = cv2.VideoCapture(0)
        webcam.set(3, 320)
        webcam.set(4, 240)
        webcam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        webcam.set(cv2.CAP_PROP_AUTO_WB, 0)
        
        # Initialize color detection
        _, initial_frame = webcam.read()
        color_thread = scanColor()
        color_thread.frame = initial_frame
        color_thread.start()
        
        print("Color detection test started. Press 'q' to quit.")
        time.sleep(1)
        
        while True:
            _, frame = webcam.read()
            color_thread.frame = frame
            
            # Display results
            print(f"Detected color: {color_thread.color}")
            if color_thread.avg_color is not None:
                print(f"Average HSV: {color_thread.avg_color}")
            
            # Show original and cropped frames
            cv2.imshow("Camera Feed", frame)
            if color_thread.cropped_image is not None:
                cv2.imshow("Detection Region", color_thread.cropped_image)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("Test interrupted by user")
    finally:
        if 'color_thread' in locals():
            color_thread.stop()
        if 'webcam' in locals():
            webcam.release()
        cv2.destroyAllWindows()
        print("Color detection test complete")

