"""
Ultrasonic Distance Sensor Module for FALCON Robot

This module provides distance measurement functionality using an HC-SR04
ultrasonic sensor. It runs in a separate thread to continuously monitor
distance for obstacle detection and navigation assistance.

Author: Inelectronics Student Club
Robot: FALCON
Competition: League of Robotics 2nd Edition
"""

import RPi.GPIO as GPIO
import time
from threading import Thread


class distance(Thread):
    """
    Ultrasonic distance sensor thread for continuous distance monitoring.
    
    Uses HC-SR04 ultrasonic sensor to measure distance to obstacles.
    Provides real-time distance data for collision avoidance and navigation.
    """
    
    def __init__(self, trigger_pin=8, echo_pin=25):
        """
        Initialize distance sensor with GPIO pin configuration.
        
        Args:
            trigger_pin (int): GPIO pin for ultrasonic trigger signal
            echo_pin (int): GPIO pin for ultrasonic echo signal
        """
        self.dist = 0               # Current distance measurement in cm
        self.on = False            # Thread running flag
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        super().__init__()

    def start(self):
        """Start the distance measurement thread."""
        Thread(target=self.run, args=()).start()
        return self

    def run(self):
        """Main distance measurement loop."""
        # Configure GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        
        self.on = True
        print(f"Distance sensor started - Trigger: GPIO {self.trigger_pin}, Echo: GPIO {self.echo_pin}")
        
        while self.on:
            try:
                # Delay between measurements to reduce CPU load
                time.sleep(0.1)
                
                # Trigger ultrasonic pulse
                GPIO.output(self.trigger_pin, True)
                time.sleep(0.00001)  # 10 microsecond pulse
                GPIO.output(self.trigger_pin, False)
                
                # Measure pulse duration
                start_time = time.time()
                stop_time = time.time()
                
                # Wait for echo to start
                while GPIO.input(self.echo_pin) == 0:
                    start_time = time.time()
                
                # Wait for echo to end
                while GPIO.input(self.echo_pin) == 1:
                    stop_time = time.time()
                
                # Calculate distance
                time_elapsed = stop_time - start_time
                # Distance = (Time × Speed of Sound) / 2
                # Speed of sound = 34300 cm/s
                self.dist = (time_elapsed * 34300) / 2
                
                # Limit measurement to reasonable range (HC-SR04 specs)
                if self.dist > 400:
                    self.dist = 400  # Max range
                elif self.dist < 2:
                    self.dist = 2    # Min range
                    
            except Exception as e:
                print(f"Distance measurement error: {e}")
                self.dist = 0
        
        # Cleanup when thread stops
        time.sleep(0.15)  # Allow final measurement to complete

    def stop(self):
        """Stop distance measurement and cleanup GPIO."""
        self.on = False
        try:
            GPIO.cleanup()
            print("Distance sensor stopped and GPIO cleaned up")
        except Exception as e:
            print(f"GPIO cleanup error: {e}")

    def get_distance(self):
        """
        Get current distance measurement.
        
        Returns:
            float: Distance in centimeters, or 0 if no valid measurement
        """
        return self.dist

    def is_obstacle_detected(self, threshold=20):
        """
        Check if an obstacle is detected within threshold distance.
        
        Args:
            threshold (float): Distance threshold in centimeters
            
        Returns:
            bool: True if obstacle detected within threshold
        """
        return 0 < self.dist < threshold


# ============================================================================
# TESTING MODULE
# ============================================================================

if __name__ == '__main__':
    """Test ultrasonic distance sensor functionality."""
    print("Distance Sensor Test Module")
    
    try:
        distance_thread = distance()
        distance_thread.start()
        
        print("Distance measurement started. Press Ctrl+C to stop.")
        
        while True:
            dist = distance_thread.get_distance()
            obstacle = distance_thread.is_obstacle_detected(30)
            
            print(f"Distance: {dist:.1f} cm | Obstacle: {'YES' if obstacle else 'NO'}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Test interrupted by user")
    finally:
        if 'distance_thread' in locals():
            distance_thread.stop()
        print("Distance sensor test complete")