#!/bin/bash

# 停止 ELK 服务脚本（直接在服务器上运行）
# 使用方法：ssh 到服务器后执行此脚本

set -e

cd "$( dirname "${BASH_SOURCE[0]}" )"

echo "=========================================="
echo "停止 ELK Stack 服务"
echo "=========================================="

# 停止 ELK 服务
docker-compose -f docker-compose.all.yml --profile elk down

echo "=========================================="
echo "ELK 服务已停止"
echo "=========================================="
echo "Elasticsearch: http://101.35.135.63:9200 (已关闭)"
echo "Kibana: http://101.35.135.63:5601 (已关闭)"
echo "Logstash: 已停止"
echo ""
echo "如需重新启动 ELK，执行："
echo "docker-compose -f docker-compose.all.yml --profile elk up -d"
echo "=========================================="
