#!/usr/bin/env bash

set -x
set -e

# 从package.json中读取版本号
VERSION=$(node -p "require('./package.json').version")

rm -rf dist
mkdir dist

cd web
npm i
npm run build

cd ..

# 先删除 app/static 中的文件
rm -rf app/static/*
# 拷贝 web/dist 中的文件到 app/static 中
cp -r web/dist/* app/static

# 压缩当前目录，排除logs目录、dist目录、.git目录、web目录、docs目录
tar -czf dist/bank-book-$VERSION.tar.gz --exclude=logs --exclude=dist --exclude=.git --exclude=web --exclude=docs ./*
