#!/bin/bash

# 更新系统并安装必需的依赖
echo "更新系统并安装依赖..."
sudo apt update -y
sudo apt install -y python3 python3-pip git screen

# 克隆 Git 仓库（如果已经存在则跳过）
echo "克隆 Bitcoin-Puzzle 仓库..."
if [ ! -d "Bitcoin-Puzzle" ]; then
    git clone https://github.com/qskg8/Bitcoin-Puzzle.git
else
    echo "Bitcoin-Puzzle 已经存在，跳过克隆"
fi

# 进入项目目录
cd Bitcoin-Puzzle

# 安装 Python 必需的库
echo "安装必要的 Python 库..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "requirements.txt 文件不存在，无法安装 Python 库"
    exit 1
fi

# 启动一个新的 screen 会话，运行 btc.py 脚本
echo "启动 screen 会话并运行 btc.py..."
screen -dmS bitcoin_puzzle bash -c "python3 btc.py"

echo "一切设置完成，脚本已在 screen 会话中运行。"
