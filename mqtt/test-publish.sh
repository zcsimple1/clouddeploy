#!/bin/bash

# 发布端 - 使用设备随机ID发送测试消息

if [ -z "$1" ]; then
  echo "用法: bash test-publish.sh <设备ID>"
  echo "示例: bash test-publish.sh MO"
  exit 1
fi

DEVICE_ID=$1
MQTT_HOST="183.230.40.96"
MQTT_PORT="1883"
MQTT_USER="v6IkuqD6vh&$DEVICE_ID"
# 为随机设备生成 Token
# 注意: 这里需要先手动为该设备生成 token,或者使用产品级 token
# 先使用产品级 token 测试
MQTT_PASS="version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1772103681&method=sha1&sign=LMk4Z%2FJ0oaeY8BoEUr63M5INBeI%3D"
CLIENT_ID="pub-$DEVICE_ID-$(date +%s)"
TOPIC="\$sys/v6IkuqD6vh/$DEVICE_ID/json"
MESSAGE="{\"temperature\": 25.5, \"humidity\": 60, \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"device\": \"$DEVICE_ID\"}"

echo "=========================================="
echo "发布端 - 发送测试消息"
echo "=========================================="
echo "Device: $DEVICE_ID"
echo "User: $MQTT_USER"
echo "Client ID: $CLIENT_ID"
echo "Topic: $TOPIC"
echo "Message: $MESSAGE"
echo "=========================================="

mosquitto_pub -h "$MQTT_HOST" -p "$MQTT_PORT" \
  -u "$MQTT_USER" -P "$MQTT_PASS" \
  -i "$CLIENT_ID" \
  -t "$TOPIC" -m "$MESSAGE" -V 311

echo "消息已发送"
