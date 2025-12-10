# Chapter 01: Locomotion Systems

## Overview

This chapter explores the diverse methods by which humanoid robots achieve movement and navigate their environment. It delves into the complexities of bipedal walking, a hallmark of humanoids, covering gait generation, stability control, and dynamic balance. Beyond walking, the chapter also addresses path planning, obstacle avoidance, and the challenges of adapting locomotion to various terrains, including stairs and uneven surfaces.

## Learning Objectives

*   Understand the principles of bipedal walking gaits and their generation.
*   Grasp the concepts of dynamic balance and disturbance rejection in humanoid robots.
*   Explore whole-body control strategies for coordinated movement.
*   Learn about navigation and path planning techniques in complex environments.
*   Recognize the challenges and solutions for locomotion on stairs and uneven terrain.

## Core Concepts

### 1. Bipedal Walking Gaits and Control

**Gait Cycle Phases:**

A complete walking cycle consists of distinct phases:

| Phase | Description | Duration | Key Events |
|-------|-------------|----------|------------|
| **Heel Strike** | Initial contact | 0-10% | Heel touches ground |
| **Loading Response** | Weight acceptance | 10-30% | Full foot contact |
| **Mid Stance** | Single support | 30-50% | Body over foot |
| **Terminal Stance** | Push-off preparation | 50-70% | Heel lift begins |
| **Pre-Swing** | Toe-off | 70-90% | Foot leaves ground |
| **Swing** | Leg advancement | 90-100% | Leg moves forward |

**Gait Cycle Diagram:**

```
Bipedal Walking Gait Cycle
    │
    ├──▶ Right Leg
    │    ├── Heel Strike (0%)
    │    ├── Loading (10-30%)
    │    ├── Mid Stance (30-50%)
    │    ├── Terminal Stance (50-70%)
    │    ├── Pre-Swing (70-90%)
    │    └── Swing (90-100%)
    │
    └──▶ Left Leg
         ├── Swing (0-50%)
         └── Stance (50-100%)
```

**Walking Control Approaches:**

| Approach | Method | Advantages | Limitations |
|----------|--------|------------|-------------|
| **ZMP-Based** | Zero Moment Point control | Stable, proven | Less dynamic |
| **Whole-Body** | Full-body optimization | Natural motion | Computationally expensive |
| **CPG-Based** | Central Pattern Generators | Robust, adaptive | Less precise |
| **Reinforcement Learning** | Learned policies | Handles complexity | Requires training |

### 2. Dynamic Balance and Disturbance Rejection

**Balance Strategies:**

| Strategy | Mechanism | Response Time | Effectiveness |
|----------|-----------|---------------|--------------|
| **Ankle Strategy** | Ankle torque adjustment | Fast | Small disturbances |
| **Hip Strategy** | Hip rotation | Medium | Medium disturbances |
| **Step Strategy** | Take recovery step | Slow | Large disturbances |
| **Whole-Body** | Coordinated movement | Variable | All disturbances |

**Balance Control Architecture:**

```
Balance Control System
    │
    ├──▶ Sensor Input
    │    ├── IMU (orientation)
    │    ├── Force sensors (contact)
    │    └── Joint encoders (position)
    │
    ├──▶ State Estimation
    │    ├── Center of Mass (CoM)
    │    ├── Zero Moment Point (ZMP)
    │    └── Support polygon
    │
    ├──▶ Balance Controller
    │    ├── Ankle strategy
    │    ├── Hip strategy
    │    └── Step planner
    │
    └──▶ Actuator Output
         └── Joint torques
```

**Disturbance Rejection:**

```python
class BalanceController:
    """
    Dynamic balance control for humanoid robot
    """
    def __init__(self):
        self.com_height = 0.9  # Center of mass height (m)
        self.support_polygon = []  # Foot contact polygon
        self.max_ankle_torque = 50  # N⋅m
        self.max_hip_torque = 100  # N⋅m
    
    def calculate_zmp(self, com_pos, com_accel):
        """
        Calculate Zero Moment Point
        ZMP = CoM_x - (CoM_z / g) * CoM_accel_x
        """
        g = 9.81  # m/s²
        zmp_x = com_pos[0] - (self.com_height / g) * com_accel[0]
        zmp_y = com_pos[1] - (self.com_height / g) * com_accel[1]
        return np.array([zmp_x, zmp_y])
    
    def check_stability(self, zmp, support_polygon):
        """
        Check if ZMP is within support polygon
        """
        return point_in_polygon(zmp, support_polygon)
    
    def compute_balance_torque(self, zmp, desired_zmp, support_polygon):
        """
        Compute required torques for balance
        """
        if not self.check_stability(zmp, support_polygon):
            # ZMP outside support - need recovery
            error = zmp - desired_zmp
            
            # Ankle strategy first
            ankle_torque = np.clip(error[0] * 10, -self.max_ankle_torque, self.max_ankle_torque)
            
            # If ankle insufficient, use hip
            if abs(ankle_torque) >= self.max_ankle_torque:
                hip_torque = np.clip(error[0] * 5, -self.max_hip_torque, self.max_hip_torque)
            else:
                hip_torque = 0
            
            return {'ankle': ankle_torque, 'hip': hip_torque}
        else:
            return {'ankle': 0, 'hip': 0}
```

### 3. Whole-Body Control

Integrated control approaches that coordinate all joints of the humanoid robot (legs, torso, arms) to achieve a desired task while maintaining balance and respecting physical constraints. Prioritization of tasks (e.g., balance vs. manipulation).

### 4. Navigation and Path Planning in Complex Environments

Algorithms for robots to find optimal paths from a starting point to a destination while avoiding obstacles. Techniques like A* search, RRT (Rapidly-exploring Random Tree), and their application in dynamic and uncertain environments.

### 5. Stair Climbing and Uneven Terrain Navigation

Advanced locomotion challenges and solutions. Strategies for detecting and traversing stairs, adapting gaits to uneven or slippery surfaces, and maintaining stability during transitions between different terrains.

## Technical Deep Dive

### Zero Moment Point (ZMP) Mathematics

**ZMP Definition:**

The Zero Moment Point is the point where the net moment of all forces acting on the robot is zero:

```math
ZMP_x = \frac{\sum_{i} m_i (z_i \ddot{x}_i - x_i \ddot{z}_i + g x_i)}{\sum_{i} m_i (\ddot{z}_i + g)}
```

Where:
- `m_i` = Mass of link i
- `x_i, z_i` = Position of link i
- `g` = Gravitational acceleration

**Simplified 2D ZMP (Linear Inverted Pendulum Model):**

For a simplified model with point mass at CoM:

```math
ZMP_x = x_{CoM} - \frac{z_{CoM}}{g} \ddot{x}_{CoM}
```

**Implementation:**

```python
import numpy as np

class ZMPCalculator:
    """
    Calculate Zero Moment Point for humanoid robot
    """
    def __init__(self, com_height=0.9):
        self.com_height = com_height
        self.g = 9.81  # m/s²
    
    def calculate_zmp_2d(self, com_x, com_accel_x):
        """
        Calculate 2D ZMP using Linear Inverted Pendulum Model
        """
        zmp_x = com_x - (self.com_height / self.g) * com_accel_x
        return zmp_x
    
    def calculate_zmp_3d(self, com_pos, com_accel):
        """
        Calculate 3D ZMP
        """
        zmp_x = com_pos[0] - (self.com_height / self.g) * com_accel[0]
        zmp_y = com_pos[1] - (self.com_height / self.g) * com_accel[1]
        return np.array([zmp_x, zmp_y])
    
    def generate_zmp_trajectory(self, step_length=0.3, step_width=0.15, num_steps=4):
        """
        Generate ZMP trajectory for walking
        """
        zmp_trajectory = []
        
        for step in range(num_steps):
            # ZMP moves from heel to toe during stance
            for phase in np.linspace(0, 1, 10):
                if step % 2 == 0:  # Right foot
                    zmp_x = step * step_length + phase * step_length * 0.6
                    zmp_y = -step_width / 2
                else:  # Left foot
                    zmp_x = step * step_length + phase * step_length * 0.6
                    zmp_y = step_width / 2
                
                zmp_trajectory.append([zmp_x, zmp_y])
        
        return np.array(zmp_trajectory)
```

### Inverted Pendulum Model

**Single Mass Model:**

For balance analysis, humanoid can be modeled as inverted pendulum:

```math
\ddot{x} = \frac{g}{h} (x - x_{ZMP})
```

Where:
- `x` = CoM horizontal position
- `h` = CoM height
- `x_{ZMP}` = ZMP position

**Solution:**

```math
x(t) = x_{ZMP} + (x_0 - x_{ZMP}) \cosh(\omega t) + \frac{\dot{x}_0}{\omega} \sinh(\omega t)
```

Where `ω = √(g/h)` is the natural frequency.

## Real-World Application

An example of a humanoid robot assisting in disaster relief, navigating rubble and climbing stairs to reach trapped individuals, showcasing robust and adaptive locomotion.

## Hands-On Exercise

**Exercise:** Imagine a simplified 2D bipedal robot. Sketch a sequence of key poses and contact points for one step of a walking gait. Discuss how the Center of Mass (CoM) and Zero Moment Point (ZMP) would need to be controlled for stability.

## Summary

Locomotion systems are central to a humanoid robot's ability to operate in human environments. This chapter provided a comprehensive look at the intricate control strategies for bipedal walking, dynamic balance, and navigating challenging terrains, highlighting the continuous progress towards more agile and robust humanoid movement.

## References

*   (Placeholder for textbooks and research papers on bipedal locomotion, humanoid balance control, and robot navigation.)
