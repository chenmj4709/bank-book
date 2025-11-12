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

# 计算工作进程数量 (CPU核心数 - 1)
WORKERS=$(( $(nproc) - 1 ))
# 确保至少有1个工作进程
if [ $WORKERS -lt 1 ]; then
    WORKERS=1
fi

echo "启动 FastAPI 应用，使用 $WORKERS 个工作进程..."

# 直接在前台运行 gunicorn（HTTPS 服务）
exec gunicorn -w $WORKERS -k uvicorn.workers.UvicornWorker --keyfile app/certs/privkey.pem --certfile app/certs/fullchain.pem -b 0.0.0.0:8301 app.server:app --access-logfile logs/gunicorn_https_access.log --error-logfile logs/gunicorn_https_error.log

echo "服务已启动，可以通过 https://localhost:8301 访问"