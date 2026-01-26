#!/bin/bash

# 一键部署脚本：拉取代码 + 构建 + 启动

echo "================================"
echo "一键部署脚本"
echo "================================"

# 拉取所有项目的最新代码
echo ""
echo "步骤 1/3: 拉取最新代码..."
./pull-all.sh

# 构建 Docker 镜像
echo ""
echo "步骤 2/3: 构建 Docker 镜像..."
docker-compose build

# 启动容器
echo ""
echo "步骤 3/3: 启动容器..."
docker-compose up -d

echo ""
echo "================================"
echo "✅ 部署完成！"
echo "================================"
echo ""
echo "访问地址："
echo "  - 首页: http://localhost:8080/"
echo "  - ZCGames: http://localhost:8080/zcgames/"
echo "  - EduTool: http://localhost:8080/edutool/"
echo "  - WebTool: http://localhost:8080/webtool/"
echo ""
