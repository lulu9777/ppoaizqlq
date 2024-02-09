#!/usr/bin/env bash

# 激活Python虚拟环境
source /root/qqqq/venv/bin/activate

# 切换到工作目录
cd /root/qqqq/qqqq2222

# 运行Python脚本

python3 4tgcs.py > 4tgcs.log 2>&1 &
sleep 9

# 等待用户按下Enter键
read -p "Press [Enter] to continue..."