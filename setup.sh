#!/bin/bash

# 设置日志目录
mkdir -p logs

# 指定 Conda 环境路径
CONDA_ENV_PATH="/home/my/miniconda3/envs/bank-book"

# 激活 Conda 环境
source activate $CONDA_ENV_PATH

# 显示 python 版本信息
python --version

# 下载相应依赖包
pip install poetry==2.1.1
poetry install

# 启动程序
python -m app.server > logs/app.log 2>&1
