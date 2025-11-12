# Bank book

bank book

## 技术栈

### 后端
- Python
- FastAPI
- Redis/MongoDB

### 前端
- Vue.js 3
- Vite
- Tailwind CSS

  ## 快速开始

### 项目结构

```bash
bank-book/
├── app/                      # Python后端
│   ├── api/                  # 接口目录
│   ├── services/             # 服务
│   ├── static/               # 前端打包后文件目录
│   ├── tests/                # 测试目录
│   ├── config.py             # 环境配置
│   └── server.py             # 主入口文件
├── web/                      # Vue.js前端
│   ├── public/               # 静态资源
│   ├── src/                  # 源代码
│   └── package.json          # 依赖管理
├── docs/                     # 项目文档
│   ├── 设计文档/              # 总体设计、概要设计、技术预研
│   ├── 需求分析/              # 需求及计划
│   └── UI/                   # UI原型图设计
├── build/                    # 打包构建配置
├── dist/                     # 构建打包目录
└── README.md                 # 项目说明
```

### 环境要求
- Node.js 20+
- Python 3.11+
- Redis/MongoDB

### 安装与运行

1. 克隆仓库
```bash
git clone git@github.com:chenmj4709/bank-book.git
cd bank-book
```

2. 安装后端依赖
```bash
conda create -n bank-book python=3.11.5
conda activate bank-book
pip install poetry==2.1.1
poetry install
```

3. 安装前端依赖
```bash
cd web
npm install
```

4. 启动开发服务
```bash
# 启动后端服务
cd ..
python -m app.server
# 启动前端服务
cd web
npm run dev
```

5. 版本提交与构建
```bash
# 回到主目录
cd ..
# windows环境
npm run version-patch
# mac环境
npm run version-patch-mac
```

上述命令的具体流程为：
    修改package.json中的version，
    修改web/package.json中的version，
    提交并创建tag，
    ci构建发行包
项目目录下的 dist/bank-book-[版本号].tar.gz 为发行包
