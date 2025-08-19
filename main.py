"""
FALCON Robot Main Control Module

This module coordinates all robot subsystems including camera input,
line following, color detection, and motor control for autonomous
navigation in the League of Robotics competition.

Author: Inelectronics Student Club
Robot: FALCON
Competition: League of Robotics 2nd Edition
"""

# Standard library imports
import time
from time import sleep
from threading import Thread, enumerate, main_thread

# Third-party imports
import cv2
import RPi.GPIO as gpio

# Local imports
from colorDetection.colorprint import scanColor
from lineFollower import line_follow
from crossing import distance
from cameraInput import camera
import Falcon

# GPIO setup
gpio.setmode(gpio.BCM)


# Initialize robot subsystem threads
camera_thread = camera()
color_thread = scanColor()
line_thread = line_follow()
distance_thread = distance()

# Motor control configuration
MOTOR_CONFIG = {
    'max_speed': 48,
    'min_speed': 20, 
    'min_speed2': 15
}

# GPIO pin configuration
GPIO_PINS = {
    'en1': 20,
    'en2': 21,
    'in1': 17,
    'in2': 22,
    'in3': 23,
    'in4': 24
}

# Setup GPIO pins
for pin in GPIO_PINS.values():
    gpio.setup(pin, gpio.OUT)

# Initialize robot
Falcon.Stop()

# Line following parameters
IMAGE_WIDTH = 160
LINE_BOUNDS = {
    'left_most': IMAGE_WIDTH * 0.255,
    'left': IMAGE_WIDTH * 0.45,
    'center': IMAGE_WIDTH / 2,
    'right': IMAGE_WIDTH * 0.55,
    'right_most': IMAGE_WIDTH * 0.705
}

# Global state
is_stuck = False
def forward_timed(speed1, speed2, duration):
    """
    Move robot forward for a specified duration with given motor speeds.
    
    Args:
        speed1 (int): Left motor speed (0-100)
        speed2 (int): Right motor speed (0-100) 
        duration (float): Time in seconds to move
    """
    start_time = time.time()
    while time.time() - start_time < duration:
        Falcon.Forward(speed1, speed2)


def execute_color_task(color):
    """
    Execute specific tasks based on detected color.
    
    Args:
        color (str): Detected color ('R', 'G', 'B')
    """
    max_speed = MOTOR_CONFIG['max_speed']
    
    if color == 'G':  # Green: Stop for 5 seconds
        forward_timed(max_speed, max_speed, 0.3)
        forward_timed(0, 0, 5)
        forward_timed(max_speed, max_speed, 0.3)
        
    elif color == 'R':  # Red: Open door, wait, close door
        forward_timed(max_speed, max_speed, 0.3)
        Falcon.openDoor()
        forward_timed(0, 0, 5)
        Falcon.closeDoor()
        forward_timed(max_speed, max_speed, 0.3)
        
    elif color == 'B':  # Blue: Stop for 2 seconds
        forward_timed(max_speed, max_speed, 0.3)
        forward_timed(0, 0, 2)
        forward_timed(max_speed, max_speed, 0.3)


def follow_line(cx):
    """
    Control robot movement based on line position.
    
    Args:
        cx (int): X-coordinate of detected line center
    """
    max_speed = MOTOR_CONFIG['max_speed']
    min_speed = MOTOR_CONFIG['min_speed']
    min_speed2 = MOTOR_CONFIG['min_speed2']
    
    if cx < LINE_BOUNDS['left_most']:
        forward_timed(min_speed2, max_speed, 0.3)
        print("left more")
    elif LINE_BOUNDS['left_most'] <= cx <= LINE_BOUNDS['left']:
        forward_timed(min_speed, max_speed, 0.05)
        print("left")
    elif LINE_BOUNDS['left'] <= cx <= LINE_BOUNDS['right']:
        Falcon.Forward(max_speed)
        print("forward")
    elif LINE_BOUNDS['right'] <= cx <= LINE_BOUNDS['right_most']:
        forward_timed(max_speed, min_speed, 0.05)
        print("right")
    elif cx >= LINE_BOUNDS['right_most']:
        forward_timed(max_speed, min_speed2, 0.3)
        print("right more")

def main_control_loop():
    """
    Main robot control logic that processes sensor inputs and
    coordinates robot behavior.
    """
    global is_stuck
    
    try:
        # Get current sensor readings
        color = color_thread.color
        no_line = line_thread.no_line
        cx = line_thread.cx
        # dist = distance_thread.dist  # Ultrasonic sensor (currently unused)
        
        # Priority 1: Handle color-based tasks
        if color in ['R', 'G', 'B']:
            execute_color_task(color)
            
        # Priority 2: Handle line following
        elif cx is None:
            forward_timed(MOTOR_CONFIG['min_speed2'], MOTOR_CONFIG['max_speed'], 0.1)
            
        elif not no_line or is_stuck:
            if not no_line:
                is_stuck = False
            follow_line(cx)
            
        # Priority 3: Handle no line detected (stuck situation)
        else:
            forward_timed(MOTOR_CONFIG['min_speed'], MOTOR_CONFIG['min_speed'], 0.2)
            print("no line detected")
            is_stuck = True
            
    except TypeError as e:
        print(f"Sensor data error: {e}")


def initialize_robot():
    """Initialize all robot subsystems and prepare for operation."""
    print("FALCON Robot initializing...")
    
    # Start camera thread first
    camera_thread.start()
    print("Camera thread started")
    
    # Wait for camera to stabilize
    sleep(3)
    
    # Share camera frames with other threads
    color_thread.frame = camera_thread.frame
    line_thread.frame = camera_thread.frame
    
    # Start processing threads
    color_thread.start()
    line_thread.start()
    print("All threads started - Robot ready")


def shutdown_robot():
    """Safely shutdown all robot subsystems."""
    print("Shutting down robot...")
    
    # Stop all threads
    color_thread.stop()
    line_thread.stop()
    camera_thread.stop()
    
    # Cleanup GPIO
    gpio.cleanup()
    cv2.destroyAllWindows()
    
    print("Robot shutdown complete")
    
    # Wait for threads to finish
    sleep(0.5)
    
    # Force stop any remaining threads
    for thread in enumerate():
        try:
            thread.stop()
        except AttributeError:
            if thread != main_thread():
                print(f"Thread {thread.name} could not be stopped")


if __name__ == '__main__':
    try:
        initialize_robot()
        
        running = True
        while running:
            try:
                # Update frame data for processing threads
                color_thread.frame = camera_thread.frame
                line_thread.frame = camera_thread.frame
                
                # Debug output
                print(f"Line center: {line_thread.cx}")
                
                # Execute main control logic
                main_control_loop()
                
                # Check for finish condition
                if line_thread.circle:
                    running = False
                    print("Finish circle detected - Competition complete!")
                    
                # Check for manual stop
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
            except KeyboardInterrupt:
                running = False
                break
                
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        shutdown_robot()
