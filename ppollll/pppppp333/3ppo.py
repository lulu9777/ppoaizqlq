import os
import numpy as np
import pandas as pd
import sqlite3
from stable_baselines3 import PPO

# 连接到SQLite数据库
conn = sqlite3.connect('./processed_data.db')

# 载入最新的数据
data = pd.read_sql('SELECT * FROM processed_data', conn).sort_values(by='id').values
mid_game_data = pd.read_sql('SELECT * FROM mid_game_data', conn).sort_values(by='id')

# 定义模型路径并加载模型
model_path = '/root/qqqq/ppollll/models/best_model.zip'
model = PPO.load(model_path)

# 用于保存预测结果的列表
predictions = []

# 遍历数据，对每一场比赛进行预测
for i, match in enumerate(data):
    # 提取'id'并重塑数据
    id = match[0]
    match = match[1:].reshape(1, -1)  # 从index 1开始以去除'id'列
    # 使用模型进行预测
    action, _ = model.predict(match)
    # 计算半场单双
    half_score_parity = (mid_game_data.iloc[i]['half_score']) % 2
    # 将预测结果添加到列表中
    predictions.append((id, mid_game_data.iloc[i]['league_type'], mid_game_data.iloc[i]['team1'], mid_game_data.iloc[i]['team2'], half_score_parity, action))

# 将预测结果写入txt文件
with open('./predictions.txt', 'w') as f:
    for prediction in predictions:
        f.write(f"联赛类型: {prediction[1]}\n")
        f.write(f"主队名称: {prediction[2]}\n")
        f.write(f"客队名称: {prediction[3]}\n")
        f.write(f"已知的（半场）单双: {prediction[4]}\n")
        f.write(f"预测的（全场）单双: {prediction[5]}\n")
        f.write("\n")
