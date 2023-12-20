#!/bin/bash

time_limit=20

# 如果没有提供参数，或提供的参数为1，则运行第一个 Python 脚本
if [ $# -eq 0 ] || [ $1 -eq 1 ]; then
    python3 /workspaces/project/Amadeus/QianFan-agent.py $time_limit
elif [ $1 -eq 2 ]; then
    # 如果提供的参数为2，则运行第二个 Python 脚本
    python3 /workspaces/project/Amadeus/ChatGPT-agent.py $time_limit
else
    echo "无效的选项: $1"
    exit 1
fi
