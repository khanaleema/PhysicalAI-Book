# Chapter 01: Actuators & Motors

## Overview

This chapter delves into the fundamental mechanisms that enable robots to move and interact with their environment: actuation systems. It explores different types of motors, their working principles, characteristics, and how to select the right actuator for specific robotic applications. Understanding actuation is crucial for designing robots that can execute precise and dynamic physical tasks.

## Learning Objectives

* Understand the working principles of common robot motors
* Compare different motor types and their characteristics
* Learn how to select appropriate actuators for robot applications
* Recognize the relationship between motor specifications and robot performance
* Apply motor selection criteria to design decisions

## Core Concepts

### 1. Motor Types and Principles

**Motor Classification:**

| Motor Type | Principle | Control | Best For |
|-----------|-----------|---------|----------|
| **DC Motor** | Electromagnetic induction | Voltage | Simple, continuous rotation |
| **Stepper Motor** | Discrete steps | Pulse sequence | Precise positioning |
| **Servo Motor** | Closed-loop control | PWM signal | Position control |
| **Brushless DC** | Electronic commutation | 3-phase control | High performance |
| **Linear Actuator** | Linear motion | Voltage/PWM | Linear movement |

**Motor Selection Flowchart:**

```
Start: Need Actuator
    │
    ├── Need Precise Positioning?
    │   ├── Yes → Stepper Motor
    │   └── No → Continue
    │
    ├── Need High Speed?
    │   ├── Yes → Brushless DC
    │   └── No → Continue
    │
    ├── Need Position Feedback?
    │   ├── Yes → Servo Motor
    │   └── No → DC Motor
    │
    └── Select Motor
```

**Motor Comparison Table:**

| Parameter | DC Motor | Stepper | Servo | Brushless DC |
|-----------|----------|---------|-------|--------------|
| **Torque** | Medium | High | Medium | High |
| **Speed** | High | Low | Medium | Very High |
| **Precision** | Low | Very High | High | High |
| **Cost** | Low | Medium | Medium | High |
| **Control Complexity** | Low | Medium | Low | High |
| **Efficiency** | Medium | Low | Medium | High |

### 2. DC Motors

**DC Motor Principle:**

A DC motor converts electrical energy into mechanical rotation:

```
DC Motor Operation
    │
    ├──▶ Electrical Input (Voltage)
    │    └──▶ Current through windings
    │
    ├──▶ Magnetic Field Generation
    │    └──▶ Interaction with permanent magnets
    │
    └──▶ Mechanical Output (Rotation)
         └──▶ Torque and speed
```

**DC Motor Characteristics:**

```python
class DCMotor:
    """
    DC Motor model
    """
    def __init__(self, kt, ke, R, L, J, b):
        """
        Parameters:
        kt: Torque constant (N⋅m/A)
        ke: Back-EMF constant (V⋅s/rad)
        R: Resistance (Ω)
        L: Inductance (H)
        J: Moment of inertia (kg⋅m²)
        b: Damping coefficient
        """
        self.kt = kt
        self.ke = ke
        self.R = R
        self.L = L
        self.J = J
        self.b = b
    
    def calculate_torque(self, current):
        """
        Calculate motor torque from current
        τ = kt * I
        """
        return self.kt * current
    
    def calculate_back_emf(self, angular_velocity):
        """
        Calculate back-EMF voltage
        V_emf = ke * ω
        """
        return self.ke * angular_velocity
    
    def motor_equation(self, voltage, angular_velocity):
        """
        Motor voltage equation:
        V = I*R + ke*ω + L*dI/dt
        """
        current = (voltage - self.calculate_back_emf(angular_velocity)) / self.R
        torque = self.calculate_torque(current)
        return torque, current
```

**DC Motor Performance:**

| Specification | Typical Range | Application |
|---------------|---------------|-------------|
| **Voltage** | 6-24V | Small to medium robots |
| **Current** | 0.5-10A | Depends on load |
| **Speed** | 1000-10000 RPM | High-speed applications |
| **Torque** | 0.01-10 N⋅m | Varies with size |

### 3. Servo Motors

**Servo Motor Architecture:**

```
Servo Motor System
    │
    ├──▶ Motor (DC or Brushless)
    │
    ├──▶ Gearbox (Reduction)
    │    └──▶ Increases torque, reduces speed
    │
    ├──▶ Position Sensor (Encoder/Potentiometer)
    │    └──▶ Feedback signal
    │
    ├──▶ Control Circuit
    │    └──▶ PID controller
    │
    └──▶ Output Shaft
         └──▶ Controlled position
```

**Servo Control:**

Servo motors use PWM (Pulse Width Modulation) for control:

| PWM Signal | Position | Application |
|------------|----------|-------------|
| **1.0 ms** | 0° (or -90°) | Minimum position |
| **1.5 ms** | 90° (center) | Neutral position |
| **2.0 ms** | 180° (or +90°) | Maximum position |

**Servo Motor Implementation:**

```python
class ServoMotor:
    """
    Servo motor with position control
    """
    def __init__(self, min_pulse=1.0, max_pulse=2.0, center_pulse=1.5):
        self.min_pulse = min_pulse  # ms
        self.max_pulse = max_pulse  # ms
        self.center_pulse = center_pulse  # ms
        self.current_position = 90  # degrees
    
    def set_position(self, target_angle):
        """
        Set servo to target angle (0-180 degrees)
        """
        # Clamp angle
        target_angle = max(0, min(180, target_angle))
        
        # Calculate PWM pulse width
        pulse_width = self.center_pulse + (target_angle - 90) * \
                     (self.max_pulse - self.min_pulse) / 180
        
        # Simulate movement
        self.current_position = target_angle
        
        return pulse_width
    
    def get_position(self):
        """
        Get current servo position
        """
        return self.current_position
```

### 4. Stepper Motors

**Stepper Motor Principle:**

Stepper motors move in discrete steps:

```
Stepper Motor Operation
    │
    ├──▶ Step 1: Energize coil A
    │    └──▶ Rotor aligns with coil A
    │
    ├──▶ Step 2: Energize coil B
    │    └──▶ Rotor moves to coil B
    │
    ├──▶ Step 3: Energize coil A (reverse)
    │    └──▶ Rotor continues rotation
    │
    └──▶ Repeat for continuous rotation
```

**Stepper Motor Types:**

| Type | Steps/Revolution | Resolution | Application |
|------|------------------|------------|-------------|
| **Full Step** | 200 (1.8°) | Low | Basic positioning |
| **Half Step** | 400 (0.9°) | Medium | Better precision |
| **Microstep** | 1600+ (0.1125°+) | High | High precision |

**Stepper Control:**

```python
class StepperMotor:
    """
    Stepper motor control
    """
    def __init__(self, steps_per_revolution=200):
        self.steps_per_rev = steps_per_revolution
        self.current_step = 0
        self.microstep_mode = 1  # 1=full, 2=half, 4=quarter, etc.
    
    def step(self, direction=1, steps=1):
        """
        Move stepper motor
        direction: 1 = forward, -1 = backward
        steps: number of steps to move
        """
        self.current_step += direction * steps
        angle = (self.current_step / self.steps_per_rev) * 360
        return angle
    
    def set_microstep(self, mode):
        """
        Set microstepping mode
        """
        self.microstep_mode = mode
        effective_steps = self.steps_per_rev * mode
        return effective_steps
```

### 5. Brushless DC Motors

**BLDC Motor Advantages:**

| Advantage | Description | Impact |
|-----------|-------------|--------|
| **High Efficiency** | No brush friction | 85-95% efficiency |
| **High Speed** | Electronic commutation | 10,000+ RPM |
| **Long Life** | No brush wear | 10,000+ hours |
| **High Power Density** | Compact design | More power per size |

**BLDC Motor Structure:**

```
BLDC Motor
    │
    ├──▶ Stator (Fixed)
    │    └──▶ 3-phase windings
    │
    ├──▶ Rotor (Rotating)
    │    └──▶ Permanent magnets
    │
    └──▶ Electronic Controller
         ├──▶ Hall sensors (position feedback)
         └──▶ 3-phase inverter
```

**BLDC Control:**

```python
class BrushlessDCMotor:
    """
    Brushless DC motor control
    """
    def __init__(self, kv_rating=1000):
        """
        kv_rating: RPM per volt (no-load)
        """
        self.kv = kv_rating
        self.pole_pairs = 14  # Typical for BLDC
    
    def calculate_speed(self, voltage, load=0):
        """
        Calculate motor speed
        RPM = kv * (V - I*R) - load_factor
        """
        no_load_rpm = self.kv * voltage
        # Simplified: subtract load effect
        actual_rpm = no_load_rpm * (1 - load * 0.1)
        return actual_rpm
    
    def calculate_torque(self, current, kt):
        """
        Calculate torque from current
        τ = kt * I
        """
        return kt * current
```

## Technical Deep Dive

### Motor Selection Mathematics

**Power Requirements:**

```math
P = \tau \times \omega
```

Where:
- `P` = Power (Watts)
- `τ` = Torque (N⋅m)
- `ω` = Angular velocity (rad/s)

**Torque-Speed Relationship:**

```python
import numpy as np
import matplotlib.pyplot as plt

class MotorPerformance:
    """
    Analyze motor performance characteristics
    """
    def __init__(self, stall_torque, no_load_speed, max_power):
        self.stall_torque = stall_torque  # N⋅m at 0 RPM
        self.no_load_speed = no_load_speed  # RPM
        self.max_power = max_power  # Watts
    
    def torque_speed_curve(self):
        """
        Generate torque-speed curve
        Linear approximation: τ = τ_stall * (1 - ω/ω_max)
        """
        speeds = np.linspace(0, self.no_load_speed, 100)
        torques = self.stall_torque * (1 - speeds / self.no_load_speed)
        powers = torques * (speeds * 2 * np.pi / 60)  # Convert RPM to rad/s
        
        return {
            'speed': speeds,
            'torque': torques,
            'power': powers
        }
    
    def find_optimal_operating_point(self):
        """
        Find point of maximum power
        """
        curve = self.torque_speed_curve()
        max_power_idx = np.argmax(curve['power'])
        
        return {
            'speed': curve['speed'][max_power_idx],
            'torque': curve['torque'][max_power_idx],
            'power': curve['power'][max_power_idx]
        }
```

## Real-World Application

**Case Study: Humanoid Robot Actuator Selection**

A humanoid robot requires actuators for 28 degrees of freedom:

**Actuator Requirements:**

| Joint | Required Torque | Speed | Precision | Selected Motor |
|-------|----------------|-------|-----------|----------------|
| **Shoulder** | 15 N⋅m | 100 RPM | Medium | Brushless DC + Gearbox |
| **Elbow** | 8 N⋅m | 150 RPM | High | Servo Motor |
| **Hip** | 20 N⋅m | 80 RPM | Medium | Brushless DC + Gearbox |
| **Knee** | 12 N⋅m | 120 RPM | High | Servo Motor |
| **Ankle** | 5 N⋅m | 200 RPM | High | Servo Motor |
| **Fingers** | 0.5 N⋅m | 300 RPM | Very High | Micro Servo |

**Selection Criteria:**

```
For Each Joint:
    │
    ├── High Torque Needed?
    │   ├── Yes → Brushless DC + Gearbox
    │   └── No → Continue
    │
    ├── High Precision Needed?
    │   ├── Yes → Servo Motor
    │   └── No → Continue
    │
    └── Simple Control Needed?
        ├── Yes → DC Motor
        └── No → Stepper Motor
```

**Results:**
- **Total Actuators**: 28
- **Power Consumption**: 500W average
- **Weight**: 8 kg (actuators only)
- **Performance**: Meets all requirements

## Hands-On Exercise

**Exercise: Select Actuators for Robot Arm**

Design actuator system for a 6-DOF robot arm:

```python
class RobotArmActuatorSelection:
    """
    Select appropriate actuators for robot arm
    """
    def __init__(self):
        self.joint_requirements = {
            'base': {'torque': 50, 'speed': 60, 'precision': 'medium'},
            'shoulder': {'torque': 30, 'speed': 80, 'precision': 'medium'},
            'elbow': {'torque': 20, 'speed': 100, 'precision': 'high'},
            'wrist_pitch': {'torque': 5, 'speed': 150, 'precision': 'high'},
            'wrist_roll': {'torque': 3, 'speed': 200, 'precision': 'high'},
            'gripper': {'torque': 2, 'speed': 100, 'precision': 'very_high'}
        }
    
    def select_actuator(self, joint_name):
        """
        Select appropriate actuator for joint
        """
        req = self.joint_requirements[joint_name]
        
        if req['precision'] == 'very_high':
            return 'Micro Servo Motor'
        elif req['precision'] == 'high':
            return 'Servo Motor'
        elif req['torque'] > 25:
            return 'Brushless DC + Gearbox'
        else:
            return 'DC Motor + Encoder'
    
    def design_actuator_system(self):
        """
        Design complete actuator system
        """
        system = {}
        for joint, req in self.joint_requirements.items():
            system[joint] = {
                'actuator': self.select_actuator(joint),
                'requirements': req,
                'estimated_cost': self.estimate_cost(joint, req)
            }
        return system
    
    def estimate_cost(self, joint, requirements):
        """
        Estimate actuator cost
        """
        # Simplified cost estimation
        if requirements['precision'] == 'very_high':
            return 50  # USD
        elif requirements['precision'] == 'high':
            return 100
        elif requirements['torque'] > 25:
            return 300
        else:
            return 80
```

**Task:**
1. Analyze joint requirements
2. Select appropriate actuators
3. Calculate total system cost
4. Estimate power consumption
5. Create actuator specification table

## Summary

Key takeaways:

* Different motor types serve different applications
* DC motors: Simple, continuous rotation
* Servo motors: Precise position control
* Stepper motors: High precision, open-loop
* Brushless DC: High performance, efficiency
* Selection depends on torque, speed, precision, and cost requirements

**Next:** [Chapter 2: PID Control](./chapter02)

## References

1. Spong, M. W., et al. (2020). *Robot Modeling and Control*. Wiley.
2. Siciliano, B., & Khatib, O. (2016). *Springer Handbook of Robotics*. Springer.
3. Craig, J. J. (2005). *Introduction to Robotics*. Pearson.
