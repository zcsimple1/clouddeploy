#!/bin/bash

# EMQX 配置文件部署脚本

echo "========================================="
echo "部署 EMQX 配置文件"
echo "========================================="

# 1. 创建配置目录
echo "1. 创建配置目录..."
mkdir -p /root/data/emqx/etc
echo "✓ 配置目录创建完成"

# 2. 复制配置文件
echo "2. 复制配置文件..."
cp emqx-config/emqx.conf /root/data/emqx/etc/
echo "✓ 配置文件复制完成"

# 3. 重启 EMQX
echo "3. 重启 EMQX 容器..."
docker-compose -f docker-compose.emqx.yml down
docker-compose -f docker-compose.emqx.yml up -d

# 4. 等待启动
echo "4. 等待 EMQX 启动..."
sleep 10

# 5. 显示日志
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
