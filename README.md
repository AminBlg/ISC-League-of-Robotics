# ISC League of Robotics - FALCON Robot

[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/opencv-4.x-green.svg)](https://opencv.org/)
[![Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)

This repository contains the autonomous control software for the **FALCON robot**, representing the Inelectronics Student Club in the League of Robotics 2nd edition competition.

## 🤖 Overview

FALCON is an autonomous robot designed to navigate a track using computer vision, perform color-based tasks, and manipulate objects using a robotic arm. The robot combines multiple subsystems working in parallel through a multithreaded architecture.

### Key Features

- **Autonomous Navigation**: Line-following using computer vision
- **Color Detection**: RGB color recognition for task zones
- **Object Manipulation**: 6-DOF robotic arm control
- **Real-time Processing**: Multithreaded architecture for optimal performance
- **Hardware Integration**: Direct GPIO control for motors, sensors, and actuators

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Camera        │    │ Line Following  │    │ Color Detection │
│   Thread        │───▶│   Thread        │    │    Thread       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────┐
                    │   Main Control  │
                    │     Loop        │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐    ┌─────────────────┐
                    │ Motor Control   │    │ Arm Control     │
                    │ (Falcon.py)     │    │ & Sensors       │
                    └─────────────────┘    └─────────────────┘
```

## 🔧 Hardware Requirements

### Computing Platform
- **Raspberry Pi 4B** (recommended) or compatible SBC
- **Camera Module**: Compatible with OpenCV VideoCapture
- **MicroSD Card**: 32GB+ (Class 10 recommended)

### Motor Control
- **L298N Motor Driver** for differential drive
- **DC Motors**: 2x geared motors for locomotion
- **Servo Motors**: 6x servos for robotic arm control

### Sensors & Actuators
- **HC-SR04 Ultrasonic Sensor** for distance measurement
- **PCA9685 PWM Driver** for servo control
- **LEDs**: Status indicators and task lighting
- **Door Mechanism**: Actuated by GPIO

### Wiring Diagram
```
Raspberry Pi GPIO Pinout:
├── Motor Control (L298N)
│   ├── EN1: GPIO 20
│   ├── EN2: GPIO 21  
│   ├── IN1: GPIO 17
│   ├── IN2: GPIO 22
│   ├── IN3: GPIO 23
│   └── IN4: GPIO 24
├── Ultrasonic Sensor (HC-SR04)
│   ├── Trigger: GPIO 8
│   └── Echo: GPIO 25
├── Door Control
│   └── Door Pin: GPIO 26
└── I2C (PCA9685)
    ├── SDA: GPIO 2
    └── SCL: GPIO 3
```

## 📦 Installation & Setup

### 1. System Prerequisites

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install python3-pip python3-venv -y

# Install system libraries for OpenCV
sudo apt install python3-opencv libcv-dev libopencv-dev -y

# Install GPIO libraries
sudo apt install python3-rpi.gpio -y
```

### 2. Clone Repository

```bash
git clone https://github.com/AminBlg/ISC-League-of-Robotics.git
cd ISC-League-of-Robotics
```

### 3. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv falcon_env
source falcon_env/bin/activate

# Install required packages
pip install opencv-python numpy tinyik
pip install adafruit-circuitpython-pca9685 adafruit-blinka
```

### 4. Hardware Setup

1. **Connect motors** to L298N driver according to wiring diagram
2. **Mount camera** at optimal height for line detection
3. **Wire sensors** following GPIO pinout specifications
4. **Calibrate servos** using the arm homing functions
5. **Test motor directions** and adjust code if necessary

## 🚀 Usage

### Quick Start

```bash
# Navigate to project directory
cd ISC-League-of-Robotics

# Run the main program
python3 main.py
```

### Robot Behavior

1. **Initialization**: Camera, color detection, and line following threads start
2. **Navigation**: Robot follows the track line using computer vision
3. **Color Detection**: When colored zones are detected:
   - **Red**: Opens door, waits 5 seconds, closes door
   - **Green**: Stops for 5 seconds
   - **Blue**: Stops for 2 seconds
4. **Completion**: Stops when finish circle is detected

### Manual Testing

Test individual components:

```bash
# Test camera input
python3 cameraInput.py

# Test color detection
python3 colorDetection/colorprint.py

# Test line following
python3 lineFollower.py

# Test distance sensor
python3 crossing.py
```

## 📁 File Structure

```
ISC-League-of-Robotics/
├── main.py                 # Main control loop and coordination
├── Falcon.py              # Hardware control functions
├── lineFollower.py        # Line detection and following logic
├── cameraInput.py         # Camera thread for frame capture
├── crossing.py            # Ultrasonic distance measurement
├── colorDetection/        # Color recognition module
│   ├── __init__.py
│   ├── colorprint.py      # Main color detection class
│   └── HSV_Treshholder.py # HSV threshold calibration
├── LineTracker2.py        # Alternative line tracking implementation
└── README.md              # This documentation
```

## ⚙️ Configuration

### Camera Settings
Modify in `cameraInput.py`:
```python
self.webcam.set(3, 160)  # Width
self.webcam.set(4, 120)  # Height
self.webcam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
self.webcam.set(cv2.CAP_PROP_AUTO_WB, 0)
```

### Line Following Parameters
Adjust in `main.py`:
```python
max_speed = 48      # Maximum motor speed
min_speed = 20      # Minimum motor speed
leftBound = imageWidth * 0.45   # Left boundary
rightBound = imageWidth * 0.55  # Right boundary
```

### Color Detection Thresholds
Calibrate HSV ranges in `colorDetection/colorprint.py`:
```python
red_lower = np.array([160, 87, 111], np.uint8)
red_upper = np.array([180, 255, 255], np.uint8)
# Similar for green and blue
```

## 🛠️ Troubleshooting

### Common Issues

**Robot doesn't follow the line properly:**
- Check camera mounting angle and height
- Adjust lighting conditions
- Recalibrate HSV thresholds for line detection

**Color detection not working:**
- Verify lighting conditions are consistent
- Recalibrate color ranges using `HSV_Treshholder.py`
- Check camera focus and positioning

**Motors not responding:**
- Verify GPIO connections match the pinout
- Check motor driver power supply
- Test with simple GPIO commands

**Robot gets stuck:**
- The system includes anti-stuck logic
- Check for physical obstructions
- Verify ultrasonic sensor functionality

### Debug Mode

Enable debug output by uncommenting print statements in the respective modules, or add:
```python
cv2.imshow("debug", frame)  # Show camera feed
```

## 🏆 Competition Strategy

The robot is designed for autonomous operation in competitive environments:

1. **Consistent Performance**: Multithreaded architecture ensures real-time response
2. **Robust Navigation**: Computer vision handles various track conditions
3. **Task Execution**: Color-based task zones trigger specific behaviors
4. **Safety Features**: Distance sensing prevents collisions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create a Pull Request

## 📜 License

This project is developed for educational and competitive purposes by the Inelectronics Student Club.

## 🙋‍♂️ Support

For technical support or questions about the FALCON robot:
- Create an issue in this repository
- Contact the Inelectronics Student Club

---

**Good luck in the League of Robotics! 🏁**
