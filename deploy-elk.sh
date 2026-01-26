#!/bin/bash

# 部署 ELK 堆栈

echo "================================"
echo "部署 ELK 堆栈"
echo "================================"

echo ""
echo "步骤 1/3: 创建日志目录..."
mkdir -p logs logstash/pipeline logstash/config

echo ""
echo "步骤 2/3: 拉取 ELK 镜像..."
docker-compose -f docker-compose.elk.yml pull

echo ""
echo "步骤 3/3: 启动 ELK 服务..."
docker-compose -f docker-compose.elk.yml up -d

echo ""
echo "================================"
echo "✅ ELK 部署完成！"
echo "================================"
echo ""
echo "访问地址："
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Kibana: http://localhost:5601"
echo "  - Logstash: http://localhost:9600"
echo ""
echo "注意事项："
echo "  - 首次启动 Elasticsearch 需要等待 1-2 分钟"
echo "  - Kibana 需要 Elasticsearch 完全启动后才能访问"
echo ""
echo "常用命令："
echo "  - 查看 ELK 状态: docker-compose -f docker-compose.elk.yml ps"
echo "  - 查看 ELK 日志: docker-compose -f docker-compose.elk.yml logs -f"
echo "  - 停止 ELK: docker-compose -f docker-compose.elk.yml down"
echo ""
