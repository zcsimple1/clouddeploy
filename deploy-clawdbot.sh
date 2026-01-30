#!/bin/bash

# Clawdbot 部署脚本

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "部署 Clawdbot AI 助手"
echo "=========================================="

# 创建数据目录
echo "创建数据目录..."
ssh root@101.35.135.63 "mkdir -p /root/data/clawdbot/ollama /root/data/clawdbot/n8n"

# 上传 docker-compose 文件
echo "上传配置文件..."
scp docker-compose.clawdbot.yml root@101.35.135.63:/root/clouddeploy/

# 部署 Clawdbot
echo "部署 Clawdbot 服务..."
ssh root@101.35.135.63 << 'EOF'
cd /root/clouddeploy

# 停止旧服务（如果存在）
docker-compose -f docker-compose.clawdbot.yml down

# 拉取最新镜像
docker-compose -f docker-compose.clawdbot.yml pull

# 启动服务
docker-compose -f docker-compose.clawdbot.yml up -d

echo "=========================================="
echo "Clawdbot 部署完成！"
echo "=========================================="
echo "访问地址: http://101.35.135.63:8081"
echo "默认账号: admin"
echo "默认密码: admin"
echo ""
echo "Ollama API: http://101.35.135.63:11434"
echo ""
echo "查看服务状态: docker-compose -f docker-compose.clawdbot.yml ps"
echo "查看日志: docker-compose -f docker-compose.clawdbot.yml logs -f"
echo ""
echo "注意事项："
echo "1. 首次登录后请修改默认密码"
echo "2. 根据服务器资源（4核8G）选择合适的AI模型"
echo "3. 推荐使用轻量级模型如: llama3.2:3b, phi3:mini, gemma2:2b"
echo "=========================================="
EOF
