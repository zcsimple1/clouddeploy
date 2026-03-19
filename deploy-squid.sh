#!/bin/bash

# Squid 代理服务器部署脚本
# 使用方法：ssh 到服务器后执行此脚本
# 可选参数：IP地址（允许访问的客户端IP）

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

# 获取允许的IP地址（从参数或SSH连接信息中获取）
ALLOWED_IP=""
if [ -n "$1" ]; then
    ALLOWED_IP="$1"
else
    # 尝试从SSH连接中获取客户端IP
    SSH_CLIENT_IP=$(echo $SSH_CLIENT | awk '{print $1}')
    if [ -n "$SSH_CLIENT_IP" ]; then
        ALLOWED_IP="$SSH_CLIENT_IP"
        echo "检测到SSH客户端IP: $ALLOWED_IP"
    fi
fi

# 如果仍然没有IP，则允许所有IP
if [ -z "$ALLOWED_IP" ]; then
    echo "警告: 未指定允许的IP地址，将允许所有IP访问（生产环境不推荐）"
    echo "用法: $0 [IP地址]"
    echo "例如: $0 1.2.3.4"
    ALLOWED_IP="0.0.0.0/0"
fi

echo "=========================================="
echo "部署 Squid 代理服务器"
echo "=========================================="
echo "允许的IP地址: $ALLOWED_IP"

# 创建数据目录
echo "创建数据目录..."
mkdir -p /root/data/squid/cache /root/data/squid/logs
mkdir -p ./squid

# 设置缓存目录权限
chmod 777 /root/data/squid/cache /root/data/squid/logs

# 生成 Squid 配置文件（动态注入允许的IP）
echo "生成 Squid 配置文件..."
cat > ./squid/squid.conf <<EOF
# Squid 配置文件（自动生成）

# 端口配置
http_port 3128

# 缓存管理器
cache_manager admin@example.com

# 缓存目录
cache_dir ufs /var/spool/squid 1000 16 256

# 日志文件
cache_log /var/log/squid/cache.log
access_log /var/log/squid/access.log squid
logfile_rotate 10

# 不缓存动态内容
refresh_pattern ^ftp:		1440	20%	10080
refresh_pattern ^gopher:	1440	0%	1440
refresh_pattern -i (/cgi-bin/|\?) 0	0%	0
refresh_pattern .		0	20%	4320

# 访问控制列表
acl localnet src 10.0.0.0/8
acl localnet src 172.16.0.0/12
acl localnet src 192.168.0.0/16
acl localnet src fc00::/7
acl localnet src fe80::/10

# 动态注入允许的IP
acl allowed_ips src $ALLOWED_IP

# SSL 端口
acl SSL_ports port 443
acl Safe_ports port 80
acl Safe_ports port 21
acl Safe_ports port 443
acl Safe_ports port 70
acl Safe_ports port 210
acl Safe_ports port 1025-65535
acl Safe_ports port 280
acl Safe_ports port 488
acl Safe_ports port 591
acl Safe_ports port 777

acl CONNECT method CONNECT

# 访问控制（优先级从高到低）
http_access allow allowed_ips
http_access allow localnet
http_access allow localhost

# 拒绝非安全端口
http_access deny !Safe_ports
http_access deny CONNECT !SSL_ports

# 拒绝所有其他访问
http_access deny all

# 管理接口
http_access allow manager localhost

# 缓存管理员邮箱
cache_mgr admin@example.com

# 主机名
visible_hostname squid-proxy

# DNS 服务器
dns_nameservers 223.5.5.5 119.29.29.29

# 内存缓存
cache_mem 256 MB

# 最大对象大小
maximum_object_size 100 MB
maximum_object_size_in_memory 512 KB

# 其他设置
client_db off
memory_cache_mode always
quick_abort_min 0 KB
quick_abort_max 0 KB
EOF

echo "配置文件已生成，允许的IP: $ALLOWED_IP"

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

# 重启服务使配置生效
echo "重启服务..."
docker-compose -f docker-compose.squid.yml restart

echo "=========================================="
echo "Squid 部署完成！"
echo "=========================================="
echo ""
echo "代理端口: 101.35.135.63:3128"
echo "直接访问: http://101.35.135.63:3128"
echo ""
echo "允许的IP: $ALLOWED_IP"
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
echo ""
echo "更新允许的IP:"
echo "  ./deploy-squid.sh <新IP地址>"
echo "=========================================="
