import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import sqlite3
import os
import sys

# 读取数据
data = pd.read_csv('./transformed_data.csv')

# 只保留match_duration列为'中'的数据
mid_game_data = data[data['match_duration'] == '中'].copy()

# 检查筛选后的数据是否为空
if mid_game_data.empty:
    print("此时没有中场休息的比赛")
    sys.exit()

# 为mid_game_data添加一个唯一标识符列
mid_game_data.loc[:, 'id'] = range(len(mid_game_data))

# 删除缺失值
data = mid_game_data.dropna()

# 将match_time转换为一天中的分钟数
data.loc[:, 'match_time'] = data['match_time'].apply(lambda x: int(x.split(':')[0])*60 + int(x.split(':')[1]))

# 计算半场总分单双
data.loc[:, 'half_score_parity'] = (data['team1_half_score'] + data['team2_half_score']) % 2

# 归一化match_time
scaler_time = MinMaxScaler()
scaled_time = scaler_time.fit_transform(data[['match_time']]).astype(np.float32)

# 标签编码
encoder = LabelEncoder()
data.loc[:, 'league_type'] = encoder.fit_transform(data['league_type'])
data.loc[:, 'team1'] = encoder.fit_transform(data['team1'])
data.loc[:, 'team2'] = encoder.fit_transform(data['team2'])

# 归一化半场得分
scaler = MinMaxScaler()
scaled_half_scores = scaler.fit_transform(data[['team1_half_score', 'team2_half_score']]).astype(np.float32)

# 合并处理过的特征
processed_data = np.concatenate([data[['id', 'league_type', 'team1', 'team2']].values, scaled_half_scores, scaled_time, data[['half_score_parity']].values.astype(np.float32)], axis=1)

# 创建一个新的DataFrame，包含处理过的数据
df = pd.DataFrame(processed_data, columns=['id', 'league_type', 'team1', 'team2', 'team1_half_score', 'team2_half_score', 'match_time', 'half_score_parity'])

# 连接到SQLite数据库（如果数据库不存在，将会被创建）
conn = sqlite3.connect('./processed_data.db')

# 将DataFrame保存到SQLite数据库
df.to_sql('processed_data', conn, if_exists='replace', index=False)

# 存储中场数据
mid_game_data.to_sql('mid_game_data', conn, if_exists='replace', index=False)

# 关闭数据库连接
conn.close()
