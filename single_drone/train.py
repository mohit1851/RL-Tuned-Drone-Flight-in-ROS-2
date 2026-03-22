import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from drone_env import DronePIDEnv

def main():
    print("🚀 Initializing Drone Environment...")
    env = DronePIDEnv()
    
    print("✅ Checking API Compliance...")
    check_env(env, warn=True)
    
    print("🧠 Building the AI Brain...")
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./drone_tensorboard/")
    
    print("⏱️  Commencing 10,000 Step Training Matrix...")
    model.learn(total_timesteps=10000, tb_log_name="PPO_Drone_Stability")
    
    print("💾 Saving the Expert Brain...")
    model.save("expert_brain")
    
    print("✨ Training Complete!")

if __name__ == '__main__':
    main()
