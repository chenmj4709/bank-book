#!/usr/bin/env bash

set -x
set -e

cd web
npm i
npm run build:dev

cd ..

# 先删除 app/static 中的文件
rm -rf app/static/*
# 拷贝 web/dist 中的文件到 app/static 中
cp -r web/dist/* app/static
