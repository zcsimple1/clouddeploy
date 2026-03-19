#!/bin/bash

# Squid 代理服务器部署脚本
# 使用方法：ssh 到服务器后执行此脚本

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "=========================================="
echo "部署 Squid 代理服务器"
echo "=========================================="

# 创建数据目录
echo "创建数据目录..."
mkdir -p /root/data/squid/cache /root/data/squid/logs
mkdir -p ./squid

# 设置缓存目录权限
chmod 777 /root/data/squid/cache /root/data/squid/logs

# 停止旧服务（如果存在）
echo "停止旧服务..."
docker-compose -f docker-compose.squid.yml down

# 启动服务
echo "启动 Squid 服务..."
docker-compose -f docker-compose.squid.yml up -d

# 初始化缓存
echo "初始化缓存..."
sleep 3
docker exec squid-proxy squid -z

# 重启服务使缓存生效
echo "重启服务..."
docker-compose -f docker-compose.squid.yml restart

echo "=========================================="
echo "Squid 部署完成！"
echo "=========================================="
echo ""
echo "代理端口: 101.35.135.63:3128"
echo "直接访问: http://101.35.135.63:3128"
echo ""
echo "查看服务状态:"
echo "  docker-compose -f docker-compose.squid.yml ps"
echo ""
echo "查看日志:"
echo "  docker-compose -f docker-compose.squid.yml logs -f"
echo "  docker exec squid-proxy tail -f /var/log/squid/access.log"
echo ""
echo "客户端使用示例:"
echo "  export http_proxy=http://101.35.135.63:3128"
echo "  export https_proxy=http://101.35.135.63:3128"
echo "  curl http://example.com"
echo ""
echo "清除缓存:"
echo "  docker exec squid-proxy squid -k rotate"
echo "=========================================="
