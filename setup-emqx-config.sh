#!/bin/bash

# EMQX 部署脚本

echo "========================================="
echo "部署 EMQX"
echo "========================================="

# 1. 重启 EMQX
echo "1. 重启 EMQX 容器..."
docker-compose -f docker-compose.emqx.yml down
docker-compose -f docker-compose.emqx.yml up -d

# 2. 等待启动
echo "2. 等待 EMQX 启动..."
sleep 10

# 3. 显示日志
echo "========================================="
echo "EMQX 最新日志："
echo "========================================="
docker logs emqx --tail 30

echo ""
echo "========================================="
echo "部署完成！"
echo "========================================="
echo "访问地址: http://101.35.135.63:18083/"
echo "默认账号: admin"
echo "默认密码: public"
echo "========================================="
