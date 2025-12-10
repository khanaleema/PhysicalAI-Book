# Chapter 02: Forward Kinematics

## Overview

This chapter dives deep into forward kinematics—the process of calculating the end-effector position and orientation from known joint angles. Master this fundamental skill to understand how robot configurations map to workspace positions.

## Learning Objectives

* Calculate end-effector pose from joint angles
* Apply transformation matrices systematically
* Use Denavit-Hartenberg (DH) parameters
* Model multi-link robot chains
* Visualize robot configurations

## Core Concepts

### 1. Forward Kinematics Process

**Transformation Chain:**

```
Base Frame (B)
    │
    │ T₁ (Joint 1)
    ▼
Link 1 Frame
    │
    │ T₂ (Joint 2)
    ▼
Link 2 Frame
    │
    │ T₃ (Joint 3)
    ▼
End-Effector Frame (E)
```

**Mathematical Representation:**

```math
T_{base}^{end} = T_1 \cdot T_2 \cdot T_3 \cdot ... \cdot T_n
```

**Implementation:**

```python
import numpy as np

class ForwardKinematics:
    def __init__(self, dh_params):
        """
        Initialize with DH parameters
        """
        self.dh_params = dh_params  # List of (a, alpha, d, theta)
    
    def compute_transformation(self, a, alpha, d, theta):
        """
        Compute single link transformation matrix
        """
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        cos_alpha = np.cos(alpha)
        sin_alpha = np.sin(alpha)
        
        T = np.array([
            [cos_theta, -sin_theta*cos_alpha, sin_theta*sin_alpha, a*cos_theta],
            [sin_theta, cos_theta*cos_alpha, -cos_theta*sin_alpha, a*sin_theta],
            [0, sin_alpha, cos_alpha, d],
            [0, 0, 0, 1]
        ])
        
        return T
    
    def forward_kinematics(self, joint_angles):
        """
        Compute end-effector pose from joint angles
        """
        T = np.eye(4)  # Identity matrix
        
        for i, (a, alpha, d, theta_base) in enumerate(self.dh_params):
            # Update theta with joint angle
            theta = theta_base + joint_angles[i]
            
            # Compute transformation
            T_i = self.compute_transformation(a, alpha, d, theta)
            
            # Chain transformations
            T = T @ T_i
        
        # Extract position and orientation
        position = T[:3, 3]
        rotation = T[:3, :3]
        
        return position, rotation, T

# Example: 3-DOF robot
dh_params = [
    (0, np.pi/2, 0.3, 0),    # Joint 1
    (0.5, 0, 0, 0),          # Joint 2
    (0.4, 0, 0, 0)           # Joint 3
]

fk = ForwardKinematics(dh_params)
position, rotation, transform = fk.forward_kinematics([
    np.pi/4,  # Joint 1: 45 degrees
    np.pi/6,  # Joint 2: 30 degrees
    np.pi/3   # Joint 3: 60 degrees
])

print(f"End-effector position: {position}")
print(f"End-effector orientation:\n{rotation}")
```

### 2. Workspace Analysis

**Reachable Workspace:**

The set of all positions the end-effector can reach:

```
Workspace Types:
├── Reachable Workspace
│   └── All positions reachable with any orientation
│
├── Dexterous Workspace
│   └── Positions reachable with any orientation
│
└── Restricted Workspace
    └── Positions with limited orientations
```

**Workspace Visualization:**

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class WorkspaceAnalyzer:
    def __init__(self, robot):
        self.robot = robot
    
    def compute_workspace(self, num_samples=10000):
        """
        Sample workspace by testing random joint configurations
        """
        positions = []
        
        for _ in range(num_samples):
            # Random joint angles
            joint_angles = np.random.uniform(
                low=self.robot.joint_limits[:, 0],
                high=self.robot.joint_limits[:, 1]
            )
            
            # Compute forward kinematics
            position, _, _ = self.robot.forward_kinematics(joint_angles)
            positions.append(position)
        
        return np.array(positions)
    
    def visualize_workspace(self, positions):
        """
        Visualize 3D workspace
        """
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        ax.scatter(positions[:, 0], 
                  positions[:, 1], 
                  positions[:, 2],
                  c=positions[:, 2],
                  cmap='viridis',
                  alpha=0.6)
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('Robot Workspace')
        plt.show()
```

### 3. Multi-DOF Robot Examples

**6-DOF Industrial Robot:**

**DH Parameters Table:**

| Joint | a (m) | α (rad) | d (m) | θ (rad) |
|-------|-------|---------|-------|---------|
| 1 | 0 | π/2 | 0.3 | θ₁ |
| 2 | 0.5 | 0 | 0 | θ₂ |
| 3 | 0.4 | 0 | 0 | θ₃ |
| 4 | 0 | π/2 | 0.2 | θ₄ |
| 5 | 0 | -π/2 | 0 | θ₅ |
| 6 | 0 | 0 | 0.1 | θ₆ |

**Forward Kinematics Implementation:**

```python
class SixDOFRobot(ForwardKinematics):
    def __init__(self):
        dh_params = [
            (0, np.pi/2, 0.3, 0),
            (0.5, 0, 0, 0),
            (0.4, 0, 0, 0),
            (0, np.pi/2, 0.2, 0),
            (0, -np.pi/2, 0, 0),
            (0, 0, 0.1, 0)
        ]
        super().__init__(dh_params)
        self.joint_limits = np.array([
            [-np.pi, np.pi],      # Joint 1
            [-np.pi/2, np.pi/2], # Joint 2
            [-np.pi, np.pi],      # Joint 3
            [-np.pi, np.pi],      # Joint 4
            [-np.pi/2, np.pi/2], # Joint 5
            [-np.pi, np.pi]       # Joint 6
        ])
    
    def get_end_effector_pose(self, joint_angles):
        """
        Get complete end-effector pose
        """
        position, rotation, T = self.forward_kinematics(joint_angles)
        
        # Convert rotation matrix to Euler angles
        euler = self.rotation_to_euler(rotation)
        
        return {
            'position': position,
            'orientation': rotation,
            'euler_angles': euler,
            'transform': T
        }
```

## Technical Deep Dive

### Efficient Forward Kinematics

**Optimized Computation:**

```python
class OptimizedFK(ForwardKinematics):
    """
    Optimized forward kinematics using caching
    """
    def __init__(self, dh_params):
        super().__init__(dh_params)
        self.cache = {}
        self.precomputed_transforms = self.precompute_transforms()
    
    def precompute_transforms(self):
        """
        Precompute constant parts of transformations
        """
        transforms = []
        for a, alpha, d, _ in self.dh_params:
            # Precompute sin/cos of alpha
            cos_alpha = np.cos(alpha)
            sin_alpha = np.sin(alpha)
            
            transforms.append({
                'a': a,
                'd': d,
                'cos_alpha': cos_alpha,
                'sin_alpha': sin_alpha
            })
        
        return transforms
    
    def fast_forward_kinematics(self, joint_angles):
        """
        Optimized forward kinematics
        """
        T = np.eye(4)
        
        for i, (theta, precomp) in enumerate(zip(joint_angles, self.precomputed_transforms)):
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)
            
            # Use precomputed values
            T_i = np.array([
                [cos_theta, -sin_theta*precomp['cos_alpha'], 
                 sin_theta*precomp['sin_alpha'], precomp['a']*cos_theta],
                [sin_theta, cos_theta*precomp['cos_alpha'], 
                 -cos_theta*precomp['sin_alpha'], precomp['a']*sin_theta],
                [0, precomp['sin_alpha'], precomp['cos_alpha'], precomp['d']],
                [0, 0, 0, 1]
            ])
            
            T = T @ T_i
        
        return T
```

## Real-World Application

**Case Study: Precision Assembly Robot**

A 6-DOF robot performs precise assembly with forward kinematics:

**Accuracy Requirements:**

| Parameter | Requirement | Achieved |
|----------|-------------|----------|
| **Position Accuracy** | ±0.1 mm | ±0.05 mm |
| **Orientation Accuracy** | ±0.01° | ±0.005° |
| **Repeatability** | ±0.05 mm | ±0.02 mm |

**Performance:**
- **Assembly Success Rate**: 99.8%
- **Cycle Time**: 2.5 seconds
- **Workspace Utilization**: 85%

## Hands-On Exercise

**Exercise: Implement Forward Kinematics**

Create a forward kinematics solver:

```python
# Your implementation here
class MyForwardKinematics:
    def __init__(self, dh_params):
        pass
    
    def forward_kinematics(self, joint_angles):
        """
        TODO: Implement forward kinematics
        """
        pass
    
    def visualize_configuration(self, joint_angles):
        """
        TODO: Visualize robot configuration
        """
        pass
```

**Task:**
1. Implement forward kinematics for a 3-DOF robot
2. Test with various joint angle combinations
3. Visualize robot configurations
4. Compute workspace

## Summary

Key takeaways:

* Forward kinematics maps joint space to task space
* Transformation matrices chain robot links
* DH parameters provide systematic modeling
* Workspace analysis reveals robot capabilities
* Efficient computation enables real-time control

**Next:** [Chapter 3: Inverse Kinematics](./chapter03)

## References

1. Spong, M. W., et al. (2020). *Robot Modeling and Control*. Wiley.
2. Craig, J. J. (2005). *Introduction to Robotics*. Pearson.
