#!/bin/bash

# 重启 MQTT 桥接服务

echo "================================"
echo "重启 MQTT 桥接服务"
echo "================================"

# 停止服务
echo "1. 停止服务..."
sudo systemctl stop elk-mqtt

# 重新部署
echo "2. 重新部署..."
cd /root/workspace/clouddeploy && bash setup-mqtt.sh

# 显示服务状态
echo ""
echo "3. 服务状态："
sudo systemctl status elk-mqtt --no-pager

echo ""
echo "================================"
echo "重启完成！"
echo "================================"
echo ""
echo "查看日志："
echo "  sudo journalctl -u elk-mqtt -f"
