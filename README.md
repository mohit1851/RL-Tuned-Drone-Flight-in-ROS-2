<div align="center">
  <h1> RL-Tuned Drone Flight in ROS 2</h1>
  <p><b>A reinforcement learning project exploring PID controller tuning and headless Gazebo simulation scaling.</b></p>
</div>

##  Project Overview
This project explores the integration of **Reinforcement Learning (RL)** with a physical drone simulation using **ROS 2 Humble** and **Gazebo**. 

The main objective is to train an RL agent to tune PID controllers for a simulated drone. During the development process, an initial single-core approach was found to be heavily bottlenecked by Gazebo's physics rendering (running at ~1 FPS). To solve this, a parallelized, headless cluster was implemented using `ROS_DOMAIN_ID` and Stable Baselines 3's `SubprocVecEnv`, which successfully accelerated training by 14x. **A similar parallelized approach can be used to train any physical system—like bipedal robots, self-driving cars, or robotic arms—using Reinforcement Learning.**

###  Technical Implementations
- **Gymnasium ROS 2 Wrapper:** A custom Python environment created to bridge ROS 2 `/cmd_vel` and `/odom` topics into OpenAI Gym-compliant multidimensional spaces.
- **DDS Network Isolation:** Utilized dynamic `ROS_DOMAIN_ID` variables to launch completely independent physics simulations, preventing ROS topic cross-contamination across multiple agents.
- **Headless Physics Acceleration:** Bypassed hardcoded C++ GUI interfaces (RViz & Gazebo Client) to dedicate 100% of CPU strictly to simulation math, accelerating training and stabilizing the server under heavy parallel loads.

---

##  Results: Performance Scaling
Training robots in Gazebo is inherently slow due to graphics rendering limitations. By scaling the standard 1-core simulation to an **8-core parallel cluster**, significant performance improvements were recorded:

- **Baseline (1 Core):** ~1 FPS (10,000 steps took ~1.5 Hours).
- **Cluster (8 Cores):** 13-14 FPS (50,000 steps took ~68 Minutes).

---

##  Project Architecture
The project is divided into three different training scenarios to demonstrate how reward function variations affect flight behavior:

### 1. `/single_drone` (The Baseline)
The foundational starting point. Uses a `DummyVecEnv` to observe a single drone training. While slow (1 FPS), it serves as a straightforward baseline for understanding and debugging ROS 2 integration.

### 2. `/multi_drone` (Stability Focus)
An 8-core orchestration implementation. The reward function heavily favors maintaining a stable hover at `z=1.0` and mathematically penalizes overshoot and large errors. The resulting policy acts as a cautious, perfectly stable PID controller.

### 3. `/kamikaze` (Speed Focus)
A scenario designed to test extreme behavior manipulation. The drone ignores stability and is rewarded purely on **Time-To-Target**. The episode rapidly terminates upon target strike or crash. The RL agent successfully learned hyper-aggressive Proportional (`Kp`) tuning to rocket toward the target as fast as safely possible.

---

##  Installation & Prerequisites

**1. System Requirements:**
- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- Python 3.10+

**2. Python & System Dependencies:**
```bash
sudo apt install ros-humble-gazebo-ros-pkgs xvfb
pip install stable_baselines3 gymnasium
```

**3. The Simulation Drone Package:**
The physical drone model (`sjtu_drone`) must be cloned and built in the ROS 2 workspace before running this project:
```bash
cd ~/your_ros2_ws/src
git clone https://github.com/NovoG93/sjtu_drone.git
cd ~/your_ros2_ws
colcon build --packages-select sjtu_drone sjtu_drone_bringup sjtu_drone_control sjtu_drone_description
source install/setup.bash
```

---

##  Usage Instructions

*Note: The Python scripts automatically spawn the required headless physics engines in the background. Running `ros2 launch` manually is not required/recommended for the multi-drone scripts.*

**To Train the Kamikaze Cluster (8-Cores):**
```bash
cd kamikaze
python3 kamikaze_train.py
```

** Important Cleanup:**
Because the script launches invisible, headless Gazebo servers, failing to close them may crash subsequent runs due to memory/port overloads. It is heavily recommended to clear the background processes between training sessions:
```bash
killall -9 gzserver gzclient rviz2
```
