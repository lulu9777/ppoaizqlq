import gym
from gym import spaces
import numpy as np

class SoccerPredictionEnv(gym.Env):
    def __init__(self, data):
        self.data = data
        self.current_step = 0

        # 计算特征数量
        num_features = data.shape[1]

        # 定义观测空间和动作空间
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(num_features-1,))  # 不包括全场总分单双
        self.action_space = spaces.Discrete(2)

    def step(self, action):
        # 获取当前的观测和奖励
        observation = self.data[self.current_step, :-1]  # 不包括最后一个特征，即全场总分单双
        full_score_parity = self.data[self.current_step, -1]

        # 计算奖励
        reward = 1 if action == full_score_parity else -1

        self.current_step += 1
        done = self.current_step >= self.data.shape[0]

        # 确保返回的观测结果的形状与观测空间的形状匹配
        observation = observation.reshape(self.observation_space.shape)

        return observation, reward, done, {}

    def reset(self):
        self.current_step = 0
        # 确保返回的观测结果的形状与观测空间的形状匹配
        return self.data[self.current_step, :-1].reshape(self.observation_space.shape)

    def render(self, mode='human'):
        # 在这里，我们打印出一些有用的信息
        print(f"Step: {self.current_step}, Action: {action}, Reward: {reward}")
