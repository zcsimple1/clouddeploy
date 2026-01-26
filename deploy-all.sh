#!/bin/bash

# 一键部署所有服务（应用 + ELK）

echo "================================"
echo "一键部署所有服务"
echo "================================"

# 部署应用服务
echo ""
echo "步骤 1/4: 拉取最新代码..."
./pull-all.sh

echo ""
echo "步骤 2/4: 部署应用服务..."
docker-compose up -d --build

# 等待应用服务启动
echo ""
echo "等待应用服务启动..."
sleep 5

# 部署 ELK 服务
echo ""
echo "步骤 3/4: 部署 ELK 服务..."
./deploy-elk.sh

echo ""
echo "步骤 4/4: 配置日志采集..."
# 这里可以添加日志配置逻辑

echo ""
echo "================================"
echo "✅ 所有服务部署完成！"
echo "================================"
echo ""
echo "应用服务："
echo "  - 首页: http://localhost:8080/"
echo "  - ZCGames: http://localhost:8080/zcgames/"
echo "  - EduTool: http://localhost:8080/edutool/"
echo "  - WebTool: http://localhost:8080/webtool/"
echo ""
echo "ELK 服务："
echo "  - Elasticsearch: http://localhost:9200"
echo "  - Kibana: http://localhost:5601"
echo "  - Logstash: http://localhost:9600"
echo ""
