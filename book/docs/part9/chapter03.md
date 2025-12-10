# Chapter 03: Sim-to-Real Transfer

## Overview

This chapter addresses one of the most critical challenges in robot learning: transferring policies trained in simulation to real robots. The "reality gap" between simulation and the physical world requires sophisticated techniques to ensure successful deployment.

## Learning Objectives

* Understand the sim-to-real gap and its causes
* Learn domain randomization techniques
* Explore domain adaptation methods
* Understand system identification
* Master techniques for robust policy transfer

## Core Concepts

### 1. The Sim-to-Real Gap

**Gap Sources:**

| Source | Impact | Mitigation |
|--------|--------|------------|
| **Physics Modeling** | High | System identification |
| **Sensor Noise** | Medium | Noise injection |
| **Actuator Dynamics** | High | Actuator modeling |
| **Visual Appearance** | Medium | Domain randomization |
| **Friction & Contact** | High | Contact modeling |

**Reality Gap Visualization:**

```
Simulation                    Real World
┌─────────────┐              ┌─────────────┐
│ Perfect     │              │ Noisy       │
│ Physics     │   ────────>  │ Sensors     │
│ Clean Data  │   GAP        │ Imperfect   │
│ Idealized   │              │ Physics     │
└─────────────┘              └─────────────┘
```

### 2. Domain Randomization

Randomize simulation parameters to improve robustness:

```python
class DomainRandomization:
    def __init__(self):
        self.params = {
            'mass': (0.8, 1.2),           # ±20% mass variation
            'friction': (0.5, 1.5),       # Friction range
            'damping': (0.5, 2.0),         # Joint damping
            'sensor_noise': (0.0, 0.05),  # Sensor noise std
            'actuator_delay': (0, 0.02),  # Actuator delay (s)
            'gravity': (9.6, 10.0),       # Gravity variation
        }
    
    def randomize_env(self, env):
        # Randomize physics parameters
        for param, (min_val, max_val) in self.params.items():
            value = np.random.uniform(min_val, max_val)
            env.set_physics_param(param, value)
        
        # Randomize visual appearance
        env.randomize_visuals()
        
        return env
```

**Randomization Strategy:**

| Parameter | Range | Effect |
|-----------|-------|--------|
| Mass | ±20% | Robustness to weight changes |
| Friction | 0.5-1.5x | Surface variation |
| Sensor Noise | 0-5% | Realistic sensing |
| Actuator Delay | 0-20ms | Motor dynamics |
| Visual Texture | Random | Appearance variation |

### 3. System Identification

Identify real-world parameters for accurate simulation:

**Parameter Identification Process:**

```python
import scipy.optimize

def identify_parameters(real_robot_data, sim_env):
    """
    Identify simulation parameters from real robot data.
    """
    def cost(params):
        # Set simulation parameters
        sim_env.set_mass(params['mass'])
        sim_env.set_friction(params['friction'])
        sim_env.set_damping(params['damping'])
        
        # Run simulation with same commands
        sim_trajectory = simulate(sim_env, real_robot_data['commands'])
        
        # Compare with real trajectory
        error = np.mean((sim_trajectory - real_robot_data['states'])**2)
        return error
    
    # Initial guess
    initial_params = {
        'mass': 1.0,
        'friction': 1.0,
        'damping': 1.0
    }
    
    # Optimize
    result = scipy.optimize.minimize(
        cost,
        initial_params,
        method='BFGS'
    )
    
    return result.x
```

### 4. Progressive Transfer

Gradually move from simulation to reality:

```
Stage 1: Pure Simulation
    ↓
Stage 2: Simulation + Domain Randomization
    ↓
Stage 3: Simulation + Real Data Fine-tuning
    ↓
Stage 4: Real Robot Deployment
```

**Implementation:**
```python
class ProgressiveTransfer:
    def __init__(self):
        self.stage = 1
        
    def train(self, policy, sim_env, real_env):
        if self.stage == 1:
            # Pure simulation
            policy = train_in_sim(policy, sim_env)
            
        elif self.stage == 2:
            # Add domain randomization
            sim_env = add_randomization(sim_env)
            policy = train_in_sim(policy, sim_env)
            
        elif self.stage == 3:
            # Fine-tune on real data
            policy = fine_tune(policy, real_env, few_episodes=10)
            
        elif self.stage == 4:
            # Deploy on real robot
            deploy(policy, real_env)
            
        return policy
```

## Technical Deep Dive

### Domain Adaptation

Adapt policies using adversarial training:

**Adversarial Domain Adaptation:**

```math
L_{total} = L_{task} + \lambda L_{domain}
```

Where:
- `L_task` = Task performance loss
- `L_domain` = Domain confusion loss
- `λ` = Adaptation weight

**Implementation:**
```python
class DomainAdversarial:
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.task_predictor = TaskPredictor()
        self.domain_classifier = DomainClassifier()
    
    def forward(self, x, domain_label):
        # Extract features
        features = self.feature_extractor(x)
        
        # Task prediction
        task_pred = self.task_predictor(features)
        
        # Domain classification (with gradient reversal)
        domain_pred = self.domain_classifier(features)
        
        return task_pred, domain_pred
    
    def loss(self, task_pred, task_true, domain_pred, domain_true):
        # Task loss
        task_loss = F.cross_entropy(task_pred, task_true)
        
        # Domain loss (with reversed gradient)
        domain_loss = F.cross_entropy(domain_pred, domain_true)
        
        # Total loss
        total_loss = task_loss - lambda_domain * domain_loss
        
        return total_loss
```

### Robust Policy Training

Train policies that are robust to parameter variations:

**Robust Optimization:**

```math
\max_\theta \min_{p \in \mathcal{P}} \mathbb{E}_{p}[\sum_t r(s_t, a_t)]
```

Where `P` is the set of possible parameter values.

## Real-World Application

**Case Study: Humanoid Walking Transfer**

**Challenge:** Transfer walking policy from simulation to real humanoid.

**Approach:**
1. **System Identification**: Identified real robot parameters
2. **Domain Randomization**: Randomized mass, friction, sensor noise
3. **Progressive Transfer**: Gradual transition to real robot
4. **Fine-tuning**: 10 episodes of real-world fine-tuning

**Results:**

| Metric | Simulation Only | With Transfer | Improvement |
|--------|------------------|---------------|-------------|
| Success Rate | 15% | 85% | +70% |
| Walking Distance | 2m | 20m | 10x |
| Stability | Low | High | Significant |

**Key Factors:**
- Domain randomization was critical (40% improvement)
- System identification improved accuracy (25% improvement)
- Fine-tuning on real robot essential (15% improvement)

## Hands-On Exercise

**Exercise: Sim-to-Real Transfer for Pendulum**

1. **Train in Simulation:**
```python
# Train policy in simulation
policy = train_pendulum_policy(sim_env, steps=100000)
```

2. **Add Domain Randomization:**
```python
# Randomize simulation parameters
randomized_env = add_randomization(sim_env)
policy = train_pendulum_policy(randomized_env, steps=50000)
```

3. **Transfer to Real:**
```python
# Deploy on real pendulum
real_env = RealPendulum()
success_rate = test_policy(policy, real_env, episodes=100)
print(f"Success rate: {success_rate:.2%}")
```

**Task:**
1. Implement domain randomization
2. Test transfer success rate
3. Experiment with different randomization ranges
4. Try fine-tuning on real robot

## Summary

Key takeaways:

* Sim-to-real gap is caused by physics, sensors, and actuators
* Domain randomization improves robustness significantly
* System identification improves simulation accuracy
* Progressive transfer enables smooth deployment
* Fine-tuning on real robot is often necessary
* Robust policies generalize better to real world

## References

1. Tobin, J., et al. (2017). "Domain Randomization for Transferring Deep Neural Networks from Simulation to the Real World." *IEEE/RSJ IROS*.
2. Peng, X. B., et al. (2018). "Sim-to-Real Transfer of Robotic Control with Dynamics Randomization." *ICRA*.
3. James, S., et al. (2019). "Sim-to-Real via Sim-to-Sim: Data-efficient Robotic Grasping via Randomized-to-Canonical Adaptation Networks." *CVPR*.

