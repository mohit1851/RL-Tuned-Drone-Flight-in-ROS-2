import os
import subprocess
import time
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv

# IMPORT THE NEW KAMIKAZE ENV
from kamikaze_env import MultiDronePIDEnv

NUM_CORES = 8 

def make_env(rank):
    def _init():
        env_vars = os.environ.copy()
        env_vars['ROS_DOMAIN_ID'] = str(rank)
        gazebo_port = 11345 + rank
        env_vars['GAZEBO_MASTER_URI'] = f"http://127.0.0.1:{gazebo_port}"
        
        subprocess.Popen(
            ["ros2", "launch", "sjtu_drone_bringup", "sjtu_drone_gazebo.launch.py", "use_gui:=false"],
            env=env_vars,
            stdout=subprocess.DEVNULL,  
            stderr=subprocess.DEVNULL
        )
        
        time.sleep(30) 
        env = MultiDronePIDEnv(domain_id=rank)
        return env
    
    return _init

def main():
    print(f"🚀 Launching 8-Core KAMIKAZE Training...")
    env = SubprocVecEnv([make_env(i) for i in range(NUM_CORES)])
    
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1,
        n_steps=1024,
        batch_size=256,
        tensorboard_log="./multi_drone_tensorboard/"
    )
    
    print("🧠 Kamikaze Matrix Initialized. Beginning 50,000 steps...")
    
    # KAMIKAZE INSTANCE
    model.learn(total_timesteps=50000, tb_log_name="PPO_Kamikaze_Cluster")
    
    print("💾 Training Complete. Saving 'drone_kamikaze_expert'")
    model.save("drone_kamikaze_expert")
    
    print("🧹 Cleaning up Physics Engines...")
    os.system("killall -9 gzserver gzclient")

if __name__ == '__main__':
    main()
