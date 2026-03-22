import time
from stable_baselines3 import PPO
from drone_env import DronePIDEnv

def main():
    # 1. Connect to the Live Robot Environment
    print("🔄 Connecting to Gazebo...")
    env = DronePIDEnv()
    
    # 2. Insert the Trained Brain
    print("🧠 Loading 'expert_brain.zip'...")
    model = PPO.load("expert_brain")

    # 3. Ask it to fly!
    print("🚀 Initiating Test Flight...")
    obs, info = env.reset()
    
    # We will test it for 100 continuous steps (about 50 seconds of flight)
    for i in range(100):
        # AI looks at the observation and chooses the best PIDs instantly!
        action, _states = model.predict(obs, deterministic=True)
        
        # We send those PIDs to the physics engine
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Let's print the PIDs it chose!
        print(f"Step {i} | Alt Error: {obs[0]:.2f} | PIDs: {action}")
        
        if terminated:
            print("💥 Drone crashed! Resetting...")
            obs, info = env.reset()

if __name__ == '__main__':
    main()
