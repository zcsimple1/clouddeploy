#!/bin/bash

# 订阅端 - 使用 MO1 订阅所有设备消息

MQTT_HOST="183.230.40.96"
MQTT_PORT="1883"
MQTT_USER="v6IkuqD6vh&MO1"
MQTT_PASS="version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772103681&method=sha1&sign=jVIWU3SNYRGjVL1c3nJTVuxNa1I%3D"
MQTT_TOPICS="\$sys/v6IkuqD6vh/#"
CLIENT_ID="sub-mo1-$(date +%s)"

echo "=========================================="
echo "订阅端 - 监听 OneNET 消息"
echo "=========================================="
echo "User: $MQTT_USER"
echo "Client ID: $CLIENT_ID"
echo "Topics: $MQTT_TOPICS"
echo "=========================================="
echo "等待接收消息... (Ctrl+C 退出)"
echo ""

mosquitto_sub -h "$MQTT_HOST" -p "$MQTT_PORT" \
  -u "$MQTT_USER" -P "$MQTT_PASS" \
  -i "$CLIENT_ID" \
  -t "$MQTT_TOPICS" -v -V 311
