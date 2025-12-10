# Chapter 01: Robot Kinematics

## Overview

This chapter introduces the mathematical foundations of robot kinematics—the study of motion without considering forces. You'll learn how to describe robot position, orientation, and motion using coordinate transformations and mathematical models.

## Learning Objectives

* Understand coordinate systems and transformations
* Master forward kinematics calculations
* Learn rotation representations (Euler angles, quaternions)
* Apply homogeneous transformations
* Model robot joint configurations

## Core Concepts

### 1. Coordinate Systems and Frames

**Frame Definition:**

A coordinate frame consists of:
- **Origin**: Reference point (O)
- **Axes**: Three orthogonal vectors (X, Y, Z)
- **Orientation**: How axes are oriented in space

**Frame Representation:**

```
World Frame (W)          Robot Base Frame (B)
┌─────────────┐         ┌─────────────┐
│      Z      │         │      Z      │
│      │      │         │      │      │
│      │      │         │      │      │
│      └──X   │         │      └──X   │
│     ╱       │         │     ╱       │
│    Y        │         │    Y        │
└─────────────┘         └─────────────┘
```

**Transformation Matrix:**

```math
T = \begin{bmatrix}
R & t \\
0 & 1
\end{bmatrix}
```

Where:
- `R` = 3×3 rotation matrix
- `t` = 3×1 translation vector

### 2. Rotation Representations

**Comparison of Rotation Methods:**

| Method | Parameters | Advantages | Disadvantages |
|--------|------------|------------|---------------|
| **Euler Angles** | 3 (roll, pitch, yaw) | Intuitive, compact | Gimbal lock |
| **Rotation Matrix** | 9 (3×3 matrix) | No singularities | Redundant |
| **Quaternions** | 4 (w, x, y, z) | No gimbal lock, efficient | Less intuitive |
| **Axis-Angle** | 4 (axis + angle) | Minimal representation | Singular at 0° |

**Euler Angles to Rotation Matrix:**

```python
import numpy as np

def euler_to_rotation_matrix(roll, pitch, yaw):
    """
    Convert Euler angles (ZYX convention) to rotation matrix
    """
    # Individual rotation matrices
    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    
    R_y = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    R_z = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    # Combined rotation (ZYX order)
    R = R_z @ R_y @ R_x
    return R

# Example
rotation = euler_to_rotation_matrix(
    roll=np.pi/6,   # 30 degrees
    pitch=np.pi/4,  # 45 degrees
    yaw=np.pi/3     # 60 degrees
)
```

### 3. Forward Kinematics

**Forward Kinematics Process:**

```
Joint Angles (θ₁, θ₂, ..., θₙ)
    │
    ▼
┌─────────────────┐
│  Transformation │
│  Chain          │
└─────────────────┘
    │
    ▼
End-Effector Pose
(x, y, z, roll, pitch, yaw)
```

**2-DOF Robot Arm Example:**

```python
import numpy as np
import matplotlib.pyplot as plt

class TwoDOFRobot:
    def __init__(self, L1=1.0, L2=1.0):
        self.L1 = L1  # Link 1 length
        self.L2 = L2  # Link 2 length
    
    def forward_kinematics(self, theta1, theta2):
        """
        Calculate end-effector position from joint angles
        """
        # Joint 1 position
        x1 = self.L1 * np.cos(theta1)
        y1 = self.L1 * np.sin(theta1)
        
        # End-effector position
        x2 = x1 + self.L2 * np.cos(theta1 + theta2)
        y2 = y1 + self.L2 * np.sin(theta1 + theta2)
        
        return (x2, y2), (x1, y1)
    
    def visualize(self, theta1, theta2):
        """
        Visualize robot configuration
        """
        end_effector, joint1 = self.forward_kinematics(theta1, theta2)
        
        plt.figure(figsize=(8, 8))
        plt.plot([0, joint1[0]], [0, joint1[1]], 'b-', linewidth=3, label='Link 1')
        plt.plot([joint1[0], end_effector[0]], 
                 [joint1[1], end_effector[1]], 'r-', linewidth=3, label='Link 2')
        plt.plot(0, 0, 'ko', markersize=10, label='Base')
        plt.plot(joint1[0], joint1[1], 'go', markersize=8, label='Joint 1')
        plt.plot(end_effector[0], end_effector[1], 'ro', markersize=8, label='End-Effector')
        plt.grid(True)
        plt.axis('equal')
        plt.legend()
        plt.title(f'Robot Configuration: θ₁={np.degrees(theta1):.1f}°, θ₂={np.degrees(theta2):.1f}°')
        plt.show()

# Example usage
robot = TwoDOFRobot(L1=1.0, L2=0.8)
robot.visualize(theta1=np.pi/4, theta2=np.pi/6)
```

### 4. Denavit-Hartenberg (DH) Parameters

**DH Parameter Convention:**

| Parameter | Symbol | Description |
|-----------|--------|-------------|
| **Link Length** | a | Distance along X axis |
| **Link Twist** | α | Rotation about X axis |
| **Link Offset** | d | Distance along Z axis |
| **Joint Angle** | θ | Rotation about Z axis |

**DH Transformation Matrix:**

```math
T_i^{i-1} = \begin{bmatrix}
\cos\theta_i & -\sin\theta_i\cos\alpha_i & \sin\theta_i\sin\alpha_i & a_i\cos\theta_i \\
\sin\theta_i & \cos\theta_i\cos\alpha_i & -\cos\theta_i\sin\alpha_i & a_i\sin\theta_i \\
0 & \sin\alpha_i & \cos\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{bmatrix}
```

**Example: 3-DOF Robot DH Table:**

| Joint | a | α | d | θ |
|-------|---|---|---|----|
| 1 | 0 | 90° | d₁ | θ₁ |
| 2 | a₂ | 0 | 0 | θ₂ |
| 3 | a₃ | 0 | 0 | θ₃ |

## Technical Deep Dive

### Homogeneous Transformations

**Transformation Chain:**

```python
def compute_forward_kinematics(dh_params, joint_angles):
    """
    Compute end-effector pose using DH parameters
    """
    T = np.eye(4)  # Identity matrix
    
    for i, (a, alpha, d, theta) in enumerate(dh_params):
        # Update theta with joint angle
        theta = theta + joint_angles[i] if i < len(joint_angles) else theta
        
        # Compute transformation matrix
        T_i = np.array([
            [np.cos(theta), -np.sin(theta)*np.cos(alpha), 
             np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
            [np.sin(theta), np.cos(theta)*np.cos(alpha), 
             -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
            [0, np.sin(alpha), np.cos(alpha), d],
            [0, 0, 0, 1]
        ])
        
        # Chain transformations
        T = T @ T_i
    
    return T

# Extract position and orientation
position = T[:3, 3]
rotation = T[:3, :3]
```

## Real-World Application

**Case Study: Industrial Robot Arm**

A 6-DOF industrial robot arm uses forward kinematics for precise positioning:

**Robot Specifications:**

| Parameter | Value |
|-----------|-------|
| **DOF** | 6 |
| **Reach** | 1.5 m |
| **Payload** | 10 kg |
| **Repeatability** | ±0.1 mm |
| **Speed** | 2 m/s |

**Workspace Visualization:**

```
        Top View
    ┌─────────────┐
    │             │
    │   Workspace │
    │      ●      │  ← Robot Base
    │    ╱ ╲      │
    │   ╱   ╲     │
    │  ╱     ╲    │
    │ ╱       ╲   │
    └─────────────┘
```

**Performance:**
- **Position accuracy**: 0.1 mm
- **Orientation accuracy**: 0.01°
- **Cycle time**: 2 seconds

## Hands-On Exercise

**Exercise: Implement Forward Kinematics**

Create a forward kinematics solver for a 3-DOF robot:

```python
class ThreeDOFRobot:
    def __init__(self):
        self.dh_params = [
            (0, np.pi/2, 0.3, 0),    # Joint 1
            (0.5, 0, 0, 0),          # Joint 2
            (0.4, 0, 0, 0)           # Joint 3
        ]
    
    def forward_kinematics(self, joint_angles):
        """
        TODO: Implement forward kinematics
        Returns: (position, orientation)
        """
        # Your code here
        pass
    
    def visualize_workspace(self, num_samples=1000):
        """
        Visualize robot workspace
        """
        # Sample joint angles
        # Compute end-effector positions
        # Plot workspace
        pass
```

**Task:**
1. Implement forward kinematics
2. Visualize workspace
3. Identify reachable vs unreachable regions
4. Calculate workspace volume

## Summary

Key takeaways:

* Coordinate frames enable spatial reasoning
* Rotation can be represented multiple ways
* Forward kinematics maps joint space to task space
* DH parameters provide systematic modeling
* Homogeneous transformations chain robot links

**Next:** [Chapter 2: Forward Kinematics](./chapter02)

## References

1. Spong, M. W., et al. (2020). *Robot Modeling and Control*. Wiley.
2. Craig, J. J. (2005). *Introduction to Robotics: Mechanics and Control*. Pearson.
3. Siciliano, B., et al. (2009). *Robotics: Modelling, Planning and Control*. Springer.
