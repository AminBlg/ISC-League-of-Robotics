"""
FALCON Robot Hardware Control Module

This module provides low-level hardware control functions for the FALCON robot,
including motor control, servo operations, LED management, and sensor interfaces.

Author: Inelectronics Student Club
Robot: FALCON
Competition: League of Robotics 2nd Edition
"""

# Standard library imports
import time

# Third-party imports  
import numpy as np
import RPi.GPIO as gpio
from board import SCL, SDA
import busio

# Hardware configuration
I2C_BUS = busio.I2C(SCL, SDA)

# Timing constants for servo operations
SERVO_TIMING = {
    'short': 0.2,
    'medium': 0.7, 
    'long': 1.0,
    'extra_long': 3.0
}

# Motor driver pin configuration (L298N)
MOTOR_PINS = {
    'speed': 100,
    'en1': 20,
    'en2': 21,
    'in1': 24,  # Left motor forward
    'in2': 23,  # Left motor backward
    'in3': 22,  # Right motor forward  
    'in4': 17   # Right motor backward
}

# Door control pin
DOOR_PIN = 26

# Initialize GPIO
gpio.setmode(gpio.BCM)
for pin in MOTOR_PINS.values():
    if isinstance(pin, int):
        gpio.setup(pin, gpio.OUT)
        
gpio.setup(DOOR_PIN, gpio.OUT)

# ============================================================================
# ROBOT ARM CONTROL FUNCTIONS  
# ============================================================================

# Initialize kinematics model for 6-DOF arm
import tinyik
arm_model = tinyik.Actuator([
    "z", [0.0, 0.0, 0.25],
    "y", [13, 0.0, 0.0], 
    "y", [9.05, 0.0, 0.0],
    "x", [3.23, 0.0, 0.0],
    "y", [14, 0.0, 0.0],
])

def calculate_inverse_kinematics(x, y, z):
    """
    Calculate joint angles for given end-effector position.
    
    Args:
        x, y, z (float): Target position coordinates
        
    Returns:
        list: Joint angles in degrees
    """
    arm_model.ee = [x, y, z]
    return np.round(np.rad2deg(arm_model.angles))


def arm_home_position():
    """Move robot arm to home/safe position."""
    print("Moving arm to home position")
    # Implementation would control actual servos
    # Currently placeholder for future servo integration


def arm_camera_position():
    """Move arm to optimal camera viewing position."""
    print("Moving arm to camera position")
    # Implementation would control actual servos


def arm_pick_position():
    """Move arm to object picking position.""" 
    print("Moving arm to pick position")
    # Implementation would control actual servos


# ============================================================================
# MOTOR CONTROL FUNCTIONS
# ============================================================================

def Forward(left_speed, right_speed=None):
    """
    Move robot forward with differential speed control.
    
    Args:
        left_speed (int): Left motor speed (0-100)
        right_speed (int): Right motor speed (0-100), defaults to left_speed
    """
    if right_speed is None:
        right_speed = left_speed
        
    # Setup PWM for speed control
    pwm_left = gpio.PWM(MOTOR_PINS['en2'], 100)  
    pwm_right = gpio.PWM(MOTOR_PINS['en1'], 100)
    
    pwm_left.start(left_speed)
    time.sleep(0.01)
    pwm_right.start(right_speed)
    time.sleep(0.01)
    
    # Set motor directions for forward movement
    gpio.output(MOTOR_PINS['in1'], False)  # Right motor forward
    gpio.output(MOTOR_PINS['in2'], True)   # Right motor backward
    gpio.output(MOTOR_PINS['in3'], False)  # Left motor forward  
    gpio.output(MOTOR_PINS['in4'], True)   # Left motor backward


def Backward(speed):
    """
    Move robot backward at specified speed.
    
    Args:
        speed (int): Motor speed (0-100)
    """
    pwm_left = gpio.PWM(MOTOR_PINS['en1'], 100)
    pwm_right = gpio.PWM(MOTOR_PINS['en2'], 100)
    
    pwm_left.start(speed)
    pwm_right.start(speed)
    
    # Set motor directions for backward movement
    gpio.output(MOTOR_PINS['in1'], True)
    gpio.output(MOTOR_PINS['in2'], False)
    gpio.output(MOTOR_PINS['in3'], True)
    gpio.output(MOTOR_PINS['in4'], False)
    print("BACKWARD")


def TurnRight(left_speed, right_speed):
    """
    Turn robot right with differential speed.
    
    Args:
        left_speed (int): Left motor speed (0-100)
        right_speed (int): Right motor speed (0-100)
    """
    pwm_left = gpio.PWM(MOTOR_PINS['en1'], 100)
    pwm_right = gpio.PWM(MOTOR_PINS['en2'], 100)
    
    pwm_left.start(left_speed)
    pwm_right.start(right_speed)
    
    gpio.output(MOTOR_PINS['in1'], True)
    gpio.output(MOTOR_PINS['in2'], False)
    gpio.output(MOTOR_PINS['in3'], False)
    gpio.output(MOTOR_PINS['in4'], True)
    print("TURN RIGHT")


def TurnLeft(left_speed, right_speed):
    """
    Turn robot left with differential speed.
    
    Args:
        left_speed (int): Left motor speed (0-100)  
        right_speed (int): Right motor speed (0-100)
    """
    pwm_left = gpio.PWM(MOTOR_PINS['en1'], 100)
    pwm_right = gpio.PWM(MOTOR_PINS['en2'], 100)
    
    pwm_left.start(right_speed)
    pwm_right.start(left_speed)
    
    gpio.output(MOTOR_PINS['in1'], False)
    gpio.output(MOTOR_PINS['in2'], True)
    gpio.output(MOTOR_PINS['in3'], True)
    gpio.output(MOTOR_PINS['in4'], False)
    print("TURN LEFT")


def Stop():
    """Stop all motor movement."""
    # Stop all motor outputs
    for pin in ['in1', 'in2', 'in3', 'in4']:
        gpio.output(MOTOR_PINS[pin], False)


def Cleanup():
    """Clean up GPIO resources."""
    gpio.cleanup()


# ============================================================================
# LIGHTING CONTROL FUNCTIONS
# ============================================================================

def FrontLight():
    """Control front LED lighting."""
    print("FRONT LED ON")
    # Implementation would control actual LEDs via PWM


def BackLight():
    """Control back LED lighting."""
    print("BACK LED ON")


def RightLight():
    """Control right LED lighting."""
    print("RIGHT LED ON") 


def LeftLight():
    """Control left LED lighting."""
    print("LEFT LED ON")


# ============================================================================
# DOOR CONTROL FUNCTIONS  
# ============================================================================

def openDoor():
    """Open the robot's door mechanism."""
    gpio.output(DOOR_PIN, True)
    print("Door opened")


def closeDoor():
    """Close the robot's door mechanism."""
    gpio.output(DOOR_PIN, False)
    print("Door closed")

# ============================================================================
# MAIN MODULE FOR TESTING
# ============================================================================

if __name__ == "__main__":
    """Test module functionality."""
    print("FALCON Hardware Control Module")
    print("Testing basic motor functions...")
    
    try:
        # Test basic movement
        print("Testing forward movement...")
        Forward(50, 50)
        time.sleep(1)
        
        print("Stopping motors...")
        Stop()
        
        print("Testing door control...")
        openDoor()
        time.sleep(1)
        closeDoor()
        
        print("Hardware test complete")
        
    except KeyboardInterrupt:
        print("Test interrupted by user")
    finally:
        Stop()
        Cleanup()
