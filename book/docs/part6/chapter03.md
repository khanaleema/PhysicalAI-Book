# Chapter 03: Balance and Disturbance Rejection

## Overview

Maintaining balance is paramount for bipedal humanoid robots, especially when performing dynamic movements or operating in unpredictable environments. This chapter explores the intricate mechanisms and control strategies employed by humanoids to achieve both static and dynamic balance, and how they actively reject external disturbances. We will delve into concepts like the Center of Mass (CoM), Zero Moment Point (ZMP), and various control approaches that enable robots to stay upright and stable, even when pushed or walking on uneven terrain.

## Learning Objectives

*   Understand the fundamental concepts of robot balance and stability.
*   Grasp the relationship between Center of Mass (CoM) and Zero Moment Point (ZMP) for balance.
*   Explore different control strategies for static and dynamic balance.
*   Identify mechanisms for detecting and rejecting external disturbances.
*   Appreciate the role of sensory feedback in robust balance control.

## Core Concepts

### 1. Fundamentals of Balance and Stability

*   **Static Stability:** A robot is statically stable if its projection of the Center of Mass (CoM) onto the ground falls within its support polygon (the area formed by its contact points). Simple robots (e.g., tripods) are statically stable if their CoM is always within this polygon.
*   **Dynamic Stability:** For dynamic movements like walking or running, the CoM may leave the support polygon. Dynamic stability involves controlling the robot's motion such that its Zero Moment Point (ZMP) remains within the support region, preventing it from tipping over.

### 2. Center of Mass (CoM) and Zero Moment Point (ZMP)

*   **Center of Mass (CoM):** The average position of all the mass of the robot. Its trajectory is crucial for controlling overall motion and stability.
*   **Zero Moment Point (ZMP):** As introduced previously, the point on the ground where the net moment of all forces acting on the robot is zero. For stable dynamic motion, the ZMP must be kept within the support region.

### 3. Balance Control Strategies

*   **Position Control:** For static tasks, controlling joint positions to keep the CoM projection within the support polygon.
*   **CoM-ZMP Control:** Actively shifting the CoM or adjusting foot placement to keep the ZMP within the desired region. This often involves a Linear Inverted Pendulum Model (LIPM) for simplified CoM dynamics.
*   **Whole-Body Control (WBC):** Coordinating all robot joints (legs, torso, arms) to influence the CoM and ZMP trajectories, allowing for more agile and robust balance control, especially under disturbances.

### 4. Disturbance Detection and Rejection

*   **Disturbance Detection:** Using sensors like IMUs (accelerometers and gyroscopes) to detect unexpected changes in orientation or acceleration, and force/torque sensors at the feet to detect external forces (e.g., a push).
*   **Rejection Strategies:**
    *   **Ankle Strategy:** Small balance corrections by adjusting ankle torques.
    *   **Hip Strategy:** Larger corrections involving hip movements.
    *   **Stepping Strategy:** Taking a step to enlarge the support polygon or shift the ZMP to regain balance.
    *   **Whole-Body Momentum Regulation:** Using the robot's arms and torso to generate counter-movements to absorb or counteract disturbances.

### 5. Role of Sensory Feedback

Robust balance control heavily relies on accurate and real-time sensory information:
*   **IMUs:** Essential for estimating robot orientation and angular velocities.
*   **Force/Torque Sensors:** Provide crucial information about ground contact forces and external disturbances.
*   **Proprioceptors (Encoders):** Joint position and velocity feedback for precise body control.
*   **Vestibular Sensors (Internal IMUs):** Mimicking biological balance organs for orientation.

## Technical Deep Dive

```python
# Placeholder for Python Code: Conceptual CoM-ZMP controller (simplified)

import numpy as np

class CoMZMPController:
    def __init__(self, dt, robot_height, gravity):
        self.dt = dt
        self.h = robot_height # Simplified constant CoM height
        self.g = gravity

        # Gains for CoM position control relative to ZMP
        self.Kp_com = 1.0
        self.Kd_com = 0.5

    def calculate_com_acceleration(self, current_com_pos, current_com_vel, desired_zmp):
        # Linear Inverted Pendulum Model (LIPM) dynamics
        # x_ddot = (g/h) * (x - ZMP)

        # Desired CoM acceleration to track desired ZMP
        # Using a simple PD controller on the CoM position relative to desired ZMP
        # This is a highly simplified control law. Real systems are much more complex.
        com_error = current_com_pos - desired_zmp
        com_error_dot = current_com_vel # Assuming this is relative to a desired CoM velocity

        desired_com_accel = -self.Kp_com * com_error - self.Kd_com * com_error_dot

        return desired_com_accel

# # Example Usage (conceptual):
# # controller = CoMZMPController(dt=0.01, robot_height=0.8, gravity=9.81)
# # current_com_x = 0.1 # m
# # current_com_vx = 0.0 # m/s
# # desired_zmp_x = 0.0 # m
# #
# # desired_accel_x = controller.calculate_com_acceleration(current_com_x, current_com_vx, desired_zmp_x)
# # print(f"Desired CoM X Acceleration: {desired_accel_x:.2f} m/s^2")
```
_**Diagram Placeholder:** A diagram showing a humanoid robot in a walking stance, illustrating the CoM, ZMP, and support polygon._
_**Diagram Placeholder:** A flowchart depicting the disturbance rejection control loop, from sensor input to actuator response._

## Real-World Application

When a humanoid robot is navigating uneven terrain or is unexpectedly bumped by a person, its balance control system immediately detects the disturbance using IMUs and force sensors. It then rapidly adjusts its ankle, hip, and whole-body posture, potentially taking a quick step, to shift its ZMP back into a stable region and prevent a fall.

## Hands-On Exercise

**Exercise:** Research and explain the concept of the "capture point" in dynamic balance control for bipedal robots. How does it relate to the ZMP, and what advantages does it offer for controlling highly dynamic motions like running?

## Summary

Balance and disturbance rejection are foundational for robust humanoid robot operation. This chapter provided a deep dive into the underlying principles of CoM and ZMP, various control strategies, and the critical role of sensory feedback in enabling humanoids to maintain stability and recover from perturbations, paving the way for truly agile and resilient Physical AI systems.

## References

*   (Placeholder for textbooks and research papers on humanoid balance control, ZMP, and robust locomotion.)
