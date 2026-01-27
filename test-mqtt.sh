#!/bin/bash

# OneNET MQTT 连接测试脚本

MQTT_HOST="183.230.40.96"
MQTT_PORT="1883"
# 使用设备级连接,用户名格式: 产品ID&设备ID
MQTT_USER="v6IkuqD6vh&MO1"
# 设备级 Token，有效期为 30 天 (2026-01-27 生成)
MQTT_PASS="version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772103581&method=sha1&sign=2jY5hQW1R%2FhTRv9uEIP9ZLkcWDo%3D"
# 订阅所有设备数据
MQTT_TOPICS="\$sys/v6IkuqD6vh/#"

# 生成随机 Client ID
CLIENT_ID="test-bridge-$(date +%s)-$$"

echo "=========================================="
echo "OneNET MQTT 连接测试"
echo "=========================================="
echo "Broker: $MQTT_HOST:$MQTT_PORT"
echo "User: $MQTT_USER"
echo "Client ID: $CLIENT_ID"
echo "Topics: $MQTT_TOPICS"
echo "=========================================="
echo ""
echo "开始订阅消息... (Ctrl+C 退出)"
echo ""

mosquitto_sub -h "$MQTT_HOST" -p "$MQTT_PORT" \
  -u "$MQTT_USER" -P "$MQTT_PASS" \
  -i "$CLIENT_ID" \
  -t "$MQTT_TOPICS" -v -V 311
