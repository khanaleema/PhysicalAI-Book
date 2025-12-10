# Chapter 01: Vision Sensors & Cameras

## Overview

This chapter covers vision sensors and camera systems—the primary means by which robots perceive the visual world. You'll learn about different camera types, image processing, and how robots extract meaningful information from visual data.

## Learning Objectives

* Understand different camera types and their characteristics
* Learn image processing fundamentals
* Master computer vision techniques for robotics
* Apply vision algorithms to robot tasks
* Integrate vision systems into robots

## Core Concepts

### 1. Camera Types and Characteristics

**Camera Comparison:**

| Type | Resolution | Frame Rate | Depth | Cost | Best For |
|------|-----------|------------|-------|------|----------|
| **RGB** | High | High | No | Low | Object recognition |
| **RGB-D** | High | Medium | Yes | Medium | Manipulation, navigation |
| **Stereo** | High | Medium | Yes | Medium | Outdoor, long range |
| **Thermal** | Medium | Medium | No | High | Low light, heat detection |
| **Event** | Very High | Very High | No | High | Fast motion |

**Camera Selection Matrix:**

```
Application Requirements
    │
    ├── Need Depth Information?
    │   ├── Yes → RGB-D or Stereo
    │   └── No → RGB Camera
    │
    ├── Fast Motion?
    │   ├── Yes → Event Camera
    │   └── No → Standard Camera
    │
    ├── Low Light?
    │   ├── Yes → Thermal or Low-light Camera
    │   └── No → Standard RGB
    │
    └── Cost Constraint?
        ├── Low → RGB Camera
        └── High → Advanced Camera
```

### 2. Image Processing Pipeline

**Processing Flow:**

```
Raw Image
    │
    ▼
Preprocessing
├── Noise Reduction
├── Color Correction
└── Normalization
    │
    ▼
Feature Extraction
├── Edges
├── Corners
├── Blobs
└── Keypoints
    │
    ▼
Object Detection
├── Classification
├── Localization
└── Segmentation
    │
    ▼
3D Understanding
├── Depth Estimation
├── Pose Estimation
└── Scene Understanding
```

**Implementation:**

```python
import cv2
import numpy as np

class VisionPipeline:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.detector = self.setup_detector()
    
    def setup_detector(self):
        """
        Setup object detector (YOLO, etc.)
        """
        # Load pre-trained model
        net = cv2.dnn.readNet('yolo.weights', 'yolo.cfg')
        return net
    
    def process_frame(self):
        """
        Complete vision processing pipeline
        """
        # 1. Capture
        ret, frame = self.camera.read()
        
        # 2. Preprocess
        processed = self.preprocess(frame)
        
        # 3. Detect objects
        detections = self.detect_objects(processed)
        
        # 4. Extract 3D information
        depth_map = self.estimate_depth(processed)
        poses = self.estimate_poses(detections, depth_map)
        
        return {
            'image': processed,
            'detections': detections,
            'depth': depth_map,
            'poses': poses
        }
    
    def preprocess(self, image):
        """
        Image preprocessing
        """
        # Noise reduction
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Color correction
        corrected = cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB)
        
        # Normalization
        normalized = corrected.astype(np.float32) / 255.0
        
        return normalized
    
    def detect_objects(self, image):
        """
        Object detection using deep learning
        """
        # Prepare input
        blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416))
        self.detector.setInput(blob)
        
        # Run inference
        outputs = self.detector.forward()
        
        # Process detections
        detections = self.process_detections(outputs)
        
        return detections
    
    def estimate_depth(self, image):
        """
        Estimate depth from RGB-D or stereo
        """
        # Depth estimation algorithm
        # (Simplified - actual implementation uses stereo or RGB-D)
        depth = self.stereo_matching(image)
        return depth
```

### 3. Computer Vision for Robotics

**Common Vision Tasks:**

| Task | Method | Application |
|------|--------|-------------|
| **Object Detection** | YOLO, Faster R-CNN | Finding objects |
| **Object Tracking** | Kalman filter, DeepSORT | Following objects |
| **Pose Estimation** | PnP, Deep learning | Object orientation |
| **Semantic Segmentation** | U-Net, DeepLab | Scene understanding |
| **Optical Flow** | Lucas-Kanade, Deep | Motion estimation |

**Vision-Based Control:**

```python
class VisionBasedControl:
    """
    Control robot using vision feedback
    """
    def __init__(self, robot, camera):
        self.robot = robot
        self.camera = camera
        self.target_tracker = ObjectTracker()
    
    def visual_servoing(self, target_object):
        """
        Move robot to target using vision
        """
        while not self.reached_target():
            # Capture image
            image = self.camera.capture()
            
            # Detect target
            target_pose = self.detect_target(image, target_object)
            
            # Compute error
            error = self.compute_error(target_pose)
            
            # Generate control
            control = self.compute_control(error)
            
            # Execute
            self.robot.move(control)
```

### 4. Depth Sensing

**Depth Sensing Methods:**

| Method | Principle | Range | Accuracy | Cost |
|--------|-----------|-------|----------|------|
| **Stereo Vision** | Triangulation | 0.5-50m | Medium | Low |
| **Structured Light** | Pattern projection | 0.3-3m | High | Medium |
| **Time-of-Flight** | Light travel time | 0.1-5m | High | High |
| **LiDAR** | Laser scanning | 1-200m | Very High | Very High |

**Depth Map Processing:**

```python
class DepthProcessor:
    def __init__(self, depth_camera):
        self.camera = depth_camera
    
    def process_depth(self, depth_map):
        """
        Process depth information
        """
        # Remove noise
        filtered = cv2.bilateralFilter(depth_map, 5, 50, 50)
        
        # Compute point cloud
        point_cloud = self.depth_to_pointcloud(filtered)
        
        # Segment objects
        segments = self.segment_objects(point_cloud)
        
        # Estimate surfaces
        surfaces = self.estimate_surfaces(segments)
        
        return {
            'depth_map': filtered,
            'point_cloud': point_cloud,
            'segments': segments,
            'surfaces': surfaces
        }
```

## Technical Deep Dive

### Camera Calibration

**Calibration Process:**

```python
class CameraCalibration:
    """
    Calibrate camera for accurate measurements
    """
    def __init__(self):
        self.camera_matrix = None
        self.distortion_coeffs = None
    
    def calibrate(self, calibration_images):
        """
        Calibrate using checkerboard pattern
        """
        # Find checkerboard corners
        objpoints = []  # 3D points
        imgpoints = []  # 2D points
        
        for img in calibration_images:
            ret, corners = cv2.findChessboardCorners(img, (9, 6))
            if ret:
                objpoints.append(self.object_points)
                imgpoints.append(corners)
        
        # Calibrate
        ret, self.camera_matrix, self.distortion_coeffs, rvecs, tvecs = \
            cv2.calibrateCamera(objpoints, imgpoints, img.shape[::-1], None, None)
        
        return ret
    
    def undistort(self, image):
        """
        Remove lens distortion
        """
        undistorted = cv2.undistort(
            image,
            self.camera_matrix,
            self.distortion_coeffs
        )
        return undistorted
```

## Real-World Application

**Case Study: Vision-Guided Manipulation**

A robot uses vision to pick and place objects:

**System Architecture:**

```
RGB-D Camera
    │
    ▼
Object Detection (YOLO)
    │
    ▼
3D Pose Estimation
    │
    ▼
Grasp Planning
    │
    ▼
Robot Execution
```

**Performance:**

| Metric | Value |
|--------|-------|
| **Detection Accuracy** | 98.5% |
| **Pose Estimation Error** | ±2mm, ±1° |
| **Success Rate** | 96% |
| **Processing Time** | 50ms |

## Hands-On Exercise

**Exercise: Build Vision System**

Implement a simple vision system:

```python
class SimpleVisionSystem:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
    
    def detect_colored_object(self, color_range):
        """
        Detect object by color
        """
        ret, frame = self.camera.read()
        
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask
        mask = cv2.inRange(hsv, color_range[0], color_range[1])
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find largest contour
        if contours:
            largest = max(contours, key=cv2.contourArea)
            center = self.get_center(largest)
            return center
        
        return None
```

**Task:**
1. Implement color-based object detection
2. Track object position over time
3. Estimate object size
4. Display results with visualization

## Summary

Key takeaways:

* Cameras are primary vision sensors for robots
* Image processing extracts meaningful information
* Computer vision enables object detection and tracking
* Depth sensing provides 3D understanding
* Vision enables visual servoing and manipulation

**Next:** [Chapter 2: Inertial Measurement Units](./chapter02)

## References

1. Szeliski, R. (2010). *Computer Vision: Algorithms and Applications*. Springer.
2. Bradski, G., & Kaehler, A. (2008). *Learning OpenCV*. O'Reilly Media.
