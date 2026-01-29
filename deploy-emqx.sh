#!/bin/bash

# EMQX 私有 MQTT 服务器部署脚本
# 用途: 部署 ELK + EMQX 完整环境

set -e

echo "========================================"
echo "ELK + EMQX 部署脚本"
echo "========================================"
echo ""

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 创建数据目录
echo "1. 创建数据目录..."
mkdir -p /root/data/elk/elasticsearch
mkdir -p /root/data/elk/logstash/pipeline
mkdir -p /root/data/elk/logstash/config
mkdir -p /root/data/elk/kibana/data
mkdir -p /root/data/emqx/data
mkdir -p /root/data/emqx/log
mkdir -p /root/data/emqx/etc
chmod -R 777 /root/data/emqx
echo "✓ 数据目录创建完成"
echo ""

# 复制 Logstash 配置
echo "2. 配置 Logstash..."
if [ -d "./logstash/pipeline" ]; then
    cp -r ./logstash/pipeline/* /root/data/elk/logstash/pipeline/ 2>/dev/null || true
    echo "✓ Logstash pipeline 配置已复制"
else
    echo "⚠️  未找到 logstash/pipeline 目录"
fi

if [ -d "./logstash/config" ]; then
    cp -r ./logstash/config/* /root/data/elk/logstash/config/ 2>/dev/null || true
    echo "✓ Logstash config 配置已复制"
else
    echo "⚠️  未找到 logstash/config 目录"
fi
echo ""

# 检查是否已存在容器
echo "3. 检查现有容器..."
if docker ps -a --format '{{.Names}}' | grep -q 'elasticsearch'; then
    echo "⚠️  检测到现有 ELK 容器"
    read -p "是否停止并删除现有容器? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker compose -f docker-compose.elk.yml down
        echo "✓ 现有容器已停止"
    else
        echo "✗ 操作取消"
        exit 1
    fi
fi
echo ""

# 启动服务
echo "4. 启动 EMQX + ELK 服务..."
docker compose -f docker-compose.emqx.yml up -d

# 等待服务启动
echo ""
echo "5. 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "6. 检查服务状态..."
docker compose -f docker-compose.emqx.yml ps

echo ""
echo "========================================"
echo "部署完成！"
echo "========================================"
echo ""
echo "访问地址："
echo "  EMQX Dashboard:  http://localhost:18083"
echo "  Kibana:          http://localhost:5601"
echo "  Elasticsearch:    http://localhost:9200"
echo "  Logstash API:    http://localhost:9600"
echo ""
echo "MQTT 连接信息："
echo "  MQTT (TCP):      localhost:1883"
echo "  MQTT (TLS):      localhost:8883"
echo "  MQTT (WS):       ws://localhost:8083/mqtt"
echo "  MQTT (WSS):      wss://localhost:8084/mqtt"
echo ""
echo "EMQX 默认账号："
echo "  用户名: admin"
echo "  密码:   public"
echo ""
echo "常用命令："
echo "  查看日志: docker compose -f docker-compose.emqx.yml logs -f [emqx|elasticsearch|logstash|kibana]"
echo "  停止服务: docker compose -f docker-compose.emqx.yml down"
echo "  重启服务: docker compose -f docker-compose.emqx.yml restart"
echo "  进入容器: docker exec -it emqx sh"
echo ""
echo "========================================"
