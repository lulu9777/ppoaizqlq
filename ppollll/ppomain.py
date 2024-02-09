import os
import gym
import numpy as np
import pandas as pd
import sqlite3
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from env import SoccerPredictionEnv
import datetime
import sys

# 获取当前时间
now = datetime.datetime.now()

# 检查当前时间是否在1点到23点之间
if not (1 <= now.hour < 23):
    print("当前时间不在训练期间（1点至23点）内。程序正在退出")
    sys.exit()

# 连接到SQLite数据库
conn = sqlite3.connect('./processed_data.db')

# 载入最新的数据
data = pd.read_sql('SELECT * FROM processed_data', conn).values

# 将数据集分为训练集和验证集
train_data, eval_data = np.split(data, [int(.8*len(data))])  # 使用80%的数据作为训练集，剩余的作为验证集

# 创建环境
env = SoccerPredictionEnv(train_data)
eval_env = SoccerPredictionEnv(eval_data)

# 定义回调函数
checkpoint_callback = CheckpointCallback(save_freq=1000, save_path='./models/',
                                         name_prefix='rl_model')
eval_callback = EvalCallback(eval_env, best_model_save_path='./models/',
                             log_path='./logs/', eval_freq=500)

# 检查是否有已经存在的最优模型
best_model_path = './models/best_model.zip'
if os.path.exists(best_model_path):
    model = PPO.load(best_model_path)
    model.set_env(env)
else:
    model = PPO('MlpPolicy', env, verbose=1)

# 训练模型
model.learn(total_timesteps=10000, callback=[checkpoint_callback, eval_callback])

# 定义模型保存路径
model_path = './model.zip'

# 保存模型
model.save(model_path)

# 测试模型
num_episodes = 100
total_reward = 0
for i in range(num_episodes):
    observation = env.reset()
    while True:
        action, _ = model.predict(observation)
        observation, reward, done, info = env.step(action)
        total_reward += reward
        if done:
            break
print(f"Average reward over {num_episodes} episodes: {total_reward / num_episodes}")
