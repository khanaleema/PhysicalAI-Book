# Chapter 02: Policy Learning & Training

## Overview

This chapter dives deep into training neural network policies for robot control. You'll learn about policy architectures, training algorithms, reward design, and techniques for efficient learning. Master these concepts to train effective robot controllers.

## Learning Objectives

* Understand different policy architectures for robot control
* Learn training algorithms: PPO, SAC, TD3
* Master reward function design
* Explore curriculum learning and domain randomization
* Understand evaluation and validation of learned policies

## Core Concepts

### 1. Policy Architectures

**Policy Network Types:**

| Architecture | Use Case | Pros | Cons |
|--------------|----------|------|------|
| **MLP** | Simple tasks | Fast, simple | Limited capacity |
| **CNN** | Vision-based | Spatial features | Vision only |
| **RNN/LSTM** | Sequential | Memory | Slower training |
| **Transformer** | Complex tasks | Attention, scale | Complex, large |

**Example MLP Policy:**
```python
import torch
import torch.nn as nn

class MLPPolicy(nn.Module):
    def __init__(self, obs_dim, action_dim, hidden_dims=[256, 256]):
        super().__init__()
        layers = []
        input_dim = obs_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU()
            ])
            input_dim = hidden_dim
            
        layers.append(nn.Linear(input_dim, action_dim))
        layers.append(nn.Tanh())  # Bounded actions
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, obs):
        return self.network(obs)
```

### 2. Training Algorithms Comparison

**Algorithm Comparison Table:**

| Algorithm | Type | Sample Efficiency | Stability | Best For |
|-----------|------|-------------------|-----------|----------|
| **PPO** | On-policy | Medium | High | General purpose |
| **SAC** | Off-policy | High | High | Continuous control |
| **TD3** | Off-policy | High | Very High | Precise control |
| **DDPG** | Off-policy | High | Medium | Simple tasks |

### 3. Proximal Policy Optimization (PPO)

PPO is widely used for robot learning:

**PPO Update Rule:**
```math
L^{CLIP}(\theta) = \mathbb{E}_t[\min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t)]
```

Where:
- `r_t(θ) = π_θ(a_t|s_t) / π_θ_old(a_t|s_t)` (probability ratio)
- `Â_t` = Advantage estimate
- `ε` = Clipping parameter (typically 0.2)

**PPO Implementation:**
```python
import torch
import torch.nn.functional as F

def ppo_update(policy, old_log_probs, states, actions, advantages, epsilon=0.2):
    # Get new policy probabilities
    new_log_probs = policy.get_log_prob(states, actions)
    
    # Compute probability ratio
    ratio = torch.exp(new_log_probs - old_log_probs)
    
    # Compute clipped objective
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1 - epsilon, 1 + epsilon) * advantages
    
    # PPO loss
    loss = -torch.min(surr1, surr2).mean()
    
    return loss
```

### 4. Reward Function Design

**Reward Components for Walking:**

```python
def walking_reward(state, action, next_state):
    # Forward progress
    progress = next_state['x'] - state['x']
    
    # Stability (minimize deviation from upright)
    stability = -abs(next_state['pitch']) - abs(next_state['roll'])
    
    # Energy efficiency (penalize large torques)
    energy = -torch.sum(action ** 2) * 0.01
    
    # Survival bonus
    survival = 1.0 if not done else 0.0
    
    # Total reward
    reward = (
        10.0 * progress +      # Forward movement
        5.0 * stability +      # Balance
        energy +                # Efficiency
        survival                # Don't fall
    )
    
    return reward
```

**Reward Shaping Guidelines:**

| Component | Weight | Purpose |
|-----------|--------|---------|
| Task completion | High (10-100) | Primary objective |
| Stability | Medium (5-10) | Safety constraint |
| Efficiency | Low (0.1-1) | Optimization |
| Survival | Medium (1-5) | Avoid failure |

## Technical Deep Dive

### Soft Actor-Critic (SAC) Algorithm

SAC combines off-policy learning with entropy regularization:

**SAC Objective:**
```math
\max_\pi \mathbb{E}[\sum_t r(s_t, a_t) + \alpha \mathcal{H}(\pi(\cdot|s_t))]
```

Where `H` is entropy, encouraging exploration.

**SAC Update:**
```python
def sac_update(critic, actor, replay_buffer, alpha=0.2):
    states, actions, rewards, next_states, dones = replay_buffer.sample()
    
    # Compute target Q-values
    with torch.no_grad():
        next_actions, next_log_probs = actor.sample(next_states)
        target_q = rewards + (1 - dones) * gamma * (
            critic(next_states, next_actions) - alpha * next_log_probs
        )
    
    # Update critic
    current_q = critic(states, actions)
    critic_loss = F.mse_loss(current_q, target_q)
    
    # Update actor
    new_actions, log_probs = actor.sample(states)
    actor_loss = (alpha * log_probs - critic(states, new_actions)).mean()
    
    return critic_loss, actor_loss
```

### Curriculum Learning

Progressive difficulty increases learning efficiency:

```python
class Curriculum:
    def __init__(self):
        self.levels = [
            {'terrain': 'flat', 'disturbance': 0.0},
            {'terrain': 'slight_slope', 'disturbance': 0.1},
            {'terrain': 'rough', 'disturbance': 0.3},
            {'terrain': 'very_rough', 'disturbance': 0.5},
        ]
        self.current_level = 0
    
    def should_advance(self, success_rate):
        if success_rate > 0.8:  # 80% success
            self.current_level = min(
                self.current_level + 1, 
                len(self.levels) - 1
            )
    
    def get_params(self):
        return self.levels[self.current_level]
```

## Real-World Application

**Case Study: Training a Humanoid to Walk**

**Setup:**
- Algorithm: PPO
- Policy: MLP (256x256)
- Training: 10M steps in simulation
- Environment: Isaac Gym (2048 parallel)

**Training Progress:**

| Metric | 1M steps | 5M steps | 10M steps |
|--------|-----------|----------|-----------|
| Success Rate | 15% | 65% | 92% |
| Walking Distance | 2m | 15m | 50m+ |
| Energy Efficiency | Low | Medium | High |

**Key Insights:**
- Curriculum learning improved final performance by 30%
- Reward shaping critical for stable walking
- Domain randomization essential for sim-to-real transfer

## Hands-On Exercise

**Exercise: Train a Simple Policy**

Implement a policy to balance an inverted pendulum:

```python
import gymnasium as gym
import torch
from stable_baselines3 import PPO

# Create environment
env = gym.make('Pendulum-v1')

# Create PPO policy
policy = PPO(
    'MlpPolicy',
    env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    verbose=1
)

# Train
policy.learn(total_timesteps=100000)

# Test
obs = env.reset()
for _ in range(1000):
    action, _ = policy.predict(obs)
    obs, reward, done, _ = env.step(action)
    if done:
        obs = env.reset()
```

**Task:**
1. Train the policy to balance the pendulum
2. Experiment with different reward functions
3. Try different algorithms (PPO, SAC, TD3)
4. Compare sample efficiency and final performance

## Summary

Key takeaways:

* Choose policy architecture based on task complexity
* PPO is a good default for on-policy learning
* SAC excels for continuous control tasks
* Reward design is critical for learning success
* Curriculum learning accelerates training
* Domain randomization improves generalization

## References

1. Schulman, J., et al. (2017). "Proximal Policy Optimization Algorithms." *arXiv:1707.06347*.
2. Haarnoja, T., et al. (2018). "Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning." *ICML*.
3. Fujimoto, S., et al. (2018). "Addressing Function Approximation Error in Actor-Critic Methods." *ICML*.

