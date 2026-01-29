#!/bin/bash

# ELK MQTT 桥接脚本 - 订阅 OneNET MQTT 并发送到 Logstash
# 使用方法: bash setup-mqtt.sh [MO|MO1]

set -e

echo "================================"
echo "ELK MQTT 桥接安装脚本"
echo "================================"
echo ""

# 选择设备
DEVICE_ID=${1:-"MO"}  # 默认使用 MO，可通过参数指定 MO1

echo "使用设备: $DEVICE_ID"
echo ""

# 根据 DEVICE_ID 选择配置
if [ "$DEVICE_ID" = "MO1" ]; then
    # MO1 配置 (设备级 Token)
    MQTT_HOST="mqtts.heclouds.com"
    MQTT_PORT="1883"
    MQTT_USER="v6IkuqD6vh"
    MQTT_PASS="version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772105871&method=sha1&sign=ZZoc17%2BbrxprIZ7prgo82Y%2FTDG4%3D"
    CLIENT_ID="MO1"
elif [ "$DEVICE_ID" = "MO" ]; then
    # MO 配置 (产品级 Token)
    MQTT_HOST="mqtts.heclouds.com"
    MQTT_PORT="1883"
    MQTT_USER="v6IkuqD6vh"
    MQTT_PASS="version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
    CLIENT_ID="MO"
else
    echo "错误: 不支持的设备 ID，请使用 MO 或 MO1"
    exit 1
fi

# 订阅主题 (OneNET 物模型主题)
MQTT_TOPICS="\$sys/v6IkuqD6vh/${DEVICE_ID}/thing/#"
LOGSTASH_URL="http://localhost:5000"
INSTALL_DIR="/root/workspace/clouddeploy/mqtt/elk-mqtt"

# 1. 创建目录
echo "1. 创建安装目录..."
mkdir -p "$INSTALL_DIR"

# 2. 创建订阅脚本
echo "2. 创建 MQTT 订阅脚本..."
cat > "$INSTALL_DIR/mqtt-to-logstash.sh" << 'SCRIPT'
#!/bin/bash

MQTT_HOST="mqtts.heclouds.com"
MQTT_PORT="1883"
MQTT_USER="v6IkuqD6vh"
MQTT_PASS="version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
# 订阅所有设备数据
MQTT_TOPICS="\$sys/v6IkuqD6vh/MO/thing/#"
LOGSTASH_URL="http://localhost:5000"

# 使用设备MO作为Client ID (必须使用已注册的设备名)
CLIENT_ID="MO"

echo "=========================================="
echo "MQTT to Logstash 桥接服务启动中..."
echo "=========================================="
echo "Broker: $MQTT_HOST:$MQTT_PORT"
echo "User: $MQTT_USER"
echo "Client ID: $CLIENT_ID"
echo "Topics: $MQTT_TOPICS"
echo "Logstash: $LOGSTASH_URL"
echo "=========================================="
echo ""

mosquitto_sub -h "$MQTT_HOST" -p "$MQTT_PORT" \
  -u "$MQTT_USER" -P "$MQTT_PASS" \
  -i "$CLIENT_ID" \
  -t "$MQTT_TOPICS" -v -V 311 2>&1 | \
  while IFS= read -r line; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] Received: $line"

    # 检查是否是 JSON 消息
    if echo "$line" | jq -e . > /dev/null 2>&1; then
      echo "[$TIMESTAMP] Sending JSON to Logstash..."
      HTTP_CODE=$(curl -X POST "$LOGSTASH_URL/" \
        -H "Content-Type: application/json" \
        -d "$line" \
        -s -o /dev/null -w "%{http_code}")
      echo "[$TIMESTAMP] Logstash response: HTTP $HTTP_CODE"
    else
      echo "[$TIMESTAMP] Not JSON, converting..."
      JSON_DATA="{\"message\": \"$line\", \"project\": \"onenet\", \"timestamp\": \"$(date -u '+%Y-%m-%dT%H:%M:%S.%3NZ')\"}"
      echo "[$TIMESTAMP] Sending converted JSON: $JSON_DATA"
      HTTP_CODE=$(echo "$JSON_DATA" | \
        curl -X POST "$LOGSTASH_URL/" \
          -H "Content-Type: application/json" \
          -d @- \
          -s -o /dev/null -w "%{http_code}")
      echo "[$TIMESTAMP] Logstash response: HTTP $HTTP_CODE"
    fi
  done
SCRIPT

chmod +x "$INSTALL_DIR/mqtt-to-logstash.sh"

# 3. 创建 systemd 服务
echo "3. 创建 systemd 服务..."
cat > /tmp/elk-mqtt.service << SERVICE
[Unit]
Description=ELK MQTT to Logstash Bridge
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/mqtt-to-logstash.sh
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE

sudo mv /tmp/elk-mqtt.service /etc/systemd/system/elk-mqtt.service

# 4. 重载 systemd
echo "4. 重载 systemd..."
sudo systemctl daemon-reload

# 5. 停止旧服务
echo "5. 停止旧服务..."
sudo systemctl stop elk-mqtt 2>/dev/null || true

# 6. 启动服务
echo "6. 启动 MQTT 桥接服务..."
sudo systemctl start elk-mqtt

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "使用设备: $DEVICE_ID"
echo "订阅主题: $MQTT_TOPICS"
echo ""
echo "常用命令："
echo "  查看服务状态:  sudo systemctl status elk-mqtt"
echo "  查看服务日志:  sudo journalctl -u elk-mqtt -f"
echo "  停止服务:     sudo systemctl stop elk-mqtt"
echo "  启动服务:     sudo systemctl start elk-mqtt"
echo "  重启服务:     sudo systemctl restart elk-mqtt"
echo ""
echo "切换设备:"
echo "  使用 MO:  sudo bash setup-mqtt.sh MO"
echo "  使用 MO1: sudo bash setup-mqtt.sh MO1"
echo ""
echo "查看服务状态..."
sudo systemctl status elk-mqtt.service --no-pager
echo ""
echo "查看日志（Ctrl+C 退出）："
sudo journalctl -u elk-mqtt -f -n 50
