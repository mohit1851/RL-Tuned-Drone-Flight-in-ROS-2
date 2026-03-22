import gymnasium as gym
import numpy as np
from gymnasium import spaces
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty as EmptySrv
from std_msgs.msg import Empty as EmptyMsg
import time
import threading

class DronePIDEnv(gym.Env):
    def __init__(self):
        super(DronePIDEnv, self).__init__()
        
        self.action_space = spaces.Box(low=0.0, high=20.0, shape=(3,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(2,), dtype=np.float32)
        
        if not rclpy.ok():
            rclpy.init()
            
        self.node = rclpy.create_node('drone_env_node_single')
        self.spin_thread = threading.Thread(target=self.ros_spin, daemon=True)
        self.spin_thread.start()
        
        self.reset_client = self.node.create_client(EmptySrv, '/reset_world')
        self.vel_pub = self.node.create_publisher(Twist, '/simple_drone/cmd_vel', 10)
        self.takeoff_pub = self.node.create_publisher(EmptyMsg, '/simple_drone/takeoff', 10)
        self.odom_sub = self.node.create_subscription(Odometry, '/simple_drone/odom', self._odom_callback, 10)
        
        self.current_z = 0.0
        self.current_vz = 0.0
        self.target_z = 1.0

    def ros_spin(self):
        rclpy.spin(self.node)

    def _odom_callback(self, msg):
        self.current_z = msg.pose.pose.position.z
        self.current_vz = msg.twist.twist.linear.z

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        if self.reset_client.wait_for_service(timeout_sec=2.0):
            self.reset_client.call_async(EmptySrv.Request())
            
        time.sleep(0.5)
        self.takeoff_pub.publish(EmptyMsg())
        
        msg = Twist()
        msg.linear.z = 5.0 
        for _ in range(10):
            self.vel_pub.publish(msg)
            time.sleep(0.05)
            
        timeout = time.time() + 2.0
        while self.current_z < 0.2 and time.time() < timeout:
            time.sleep(0.1)
        
        return np.array([self.target_z - self.current_z, self.current_vz], dtype=np.float32), {}

    def step(self, action):
        kp, ki, kd = action
        total_error = 0
        
        for _ in range(50):
            error = self.target_z - self.current_z
            thrust = kp * error - kd * self.current_vz 
            msg = Twist()
            msg.linear.z = float(thrust)
            self.vel_pub.publish(msg)
            time.sleep(0.01)
            total_error += abs(error)
            
        reward = -total_error
        terminated = self.current_z < 0.1 or self.current_z > 5.0
        obs = np.array([self.target_z - self.current_z, self.current_vz], dtype=np.float32)
        return obs, reward, terminated, False, {}
