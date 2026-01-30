#!/bin/bash

# Clawdbot 部署脚本（直接在服务器上运行）
# 使用方法：ssh 到服务器后执行此脚本

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "=========================================="
echo "部署 Clawdbot AI 助手"
echo "=========================================="

# 创建数据目录
echo "创建数据目录..."
mkdir -p /root/data/clawdbot/ollama /root/data/clawdbot/n8n

# 停止旧服务（如果存在）
echo "停止旧服务..."
docker-compose -f docker-compose.clawdbot.yml down

# 拉取最新镜像
echo "拉取最新镜像..."
docker-compose -f docker-compose.clawdbot.yml pull

# 启动服务
echo "启动服务..."
docker-compose -f docker-compose.clawdbot.yml up -d

echo "=========================================="
echo "Clawdbot 部署完成！"
echo "=========================================="
echo "访问地址: http://101.35.135.63:8081"
echo "默认账号: admin"
echo "默认密码: admin"
echo ""
echo "Ollama API: http://101.35.135.63:11434"
echo "n8n 工作流: http://101.35.135.63:5678"
echo ""
echo "查看服务状态: docker-compose -f docker-compose.clawdbot.yml ps"
echo "查看日志: docker-compose -f docker-compose.clawdbot.yml logs -f"
echo ""
echo "下载模型（进入容器执行）："
echo "docker exec -it clawdbot-ollama bash"
echo "ollama pull llama3.2:3b"
echo "=========================================="
