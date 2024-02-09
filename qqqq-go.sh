#!/usr/bin/env bash

# 激活Python虚拟环境
source /root/qqqq/venv/bin/activate

# 切换到工作目录
cd /root/qqqq

# 运行Python脚本

python3 1datamain.py > 1datamain.log 2>&1 &
sleep 333
python3 data_preprocessing_and_storage.py > data_preprocessing_and_storage.log 2>&1 &
sleep 222
python3 ppomain.py > ppomain.log 2>&1 &
sleep 111

# 等待用户按下Enter键
read -p "Press [Enter] to continue..."
