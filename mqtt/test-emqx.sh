#!/bin/bash

# EMQX 快速测试脚本
# 用途: 测试 EMQX MQTT 服务器是否正常工作

set -e

echo "========================================"
echo "EMQX MQTT 服务器测试"
echo "========================================"
echo ""

# 检查 EMQX 是否运行
echo "1. 检查 EMQX 状态..."
if docker ps --format '{{.Names}}' | grep -q 'emqx'; then
    echo "✓ EMQX 正在运行"
else
    echo "✗ EMQX 未运行"
    echo "请先运行: sudo bash deploy-emqx.sh"
    exit 1
fi

echo ""

# 测试 MQTT 连接
echo "2. 测试 MQTT 连接..."
if command -v nc &> /dev/null; then
    nc -zv localhost 1883
    echo "✓ MQTT 端口 1883 可访问"
elif command -v telnet &> /dev/null; then
    timeout 2 telnet localhost 1883 | head -n 1
    echo "✓ MQTT 端口 1883 可访问"
else
    echo "⚠️  无法测试端口（需要 nc 或 telnet）"
fi

echo ""

# 测试 Dashboard
echo "3. 测试 EMQX Dashboard..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:18083 | grep -q "200"; then
    echo "✓ Dashboard 可访问: http://localhost:18083"
else
    echo "✗ Dashboard 无法访问"
fi

echo ""

# Python MQTT 测试
echo "4. 测试 MQTT 发布和订阅..."
if command -v python3 &> /dev/null; then
    python3 << 'PYTHON_SCRIPT'
import paho.mqtt.client as mqtt
import time
import json

received = False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("emqx/test/#")
        print("  ✓ 已连接并订阅主题")

def on_message(client, userdata, msg):
    global received
    print(f"  ✓ 收到消息: {msg.topic} - {msg.payload.decode()}")
    received = True

client = mqtt.Client("test_client")
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_start()
time.sleep(1)

# 发布测试消息
msg = {"test": "emqx", "time": int(time.time())}
client.publish("emqx/test/ping", json.dumps(msg))
print("  ✓ 已发布测试消息")

# 等待接收
for _ in range(10):
    if received:
        break
    time.sleep(0.1)

client.loop_stop()

if received:
    print("  ✓✓✓ MQTT 发布/订阅测试成功！")
else:
    print("  ✗ 未收到消息")

PYTHON_SCRIPT
else
    echo "⚠️  未找到 Python 3，跳过 MQTT 功能测试"
    echo "请安装: pip3 install paho-mqtt"
fi

echo ""

# 测试 Logstash 集成
echo "5. 测试 Logstash 集成..."
if docker ps --format '{{.Names}}' | grep -q 'logstash'; then
    if docker exec emqx ping -c 1 logstash &> /dev/null; then
        echo "✓ EMQX 可以连接到 Logstash"
    else
        echo "⚠️  EMQX 无法连接到 Logstash"
    fi
else
    echo "⚠️  Logstash 未运行"
fi

echo ""
echo "========================================"
echo "测试完成"
echo "========================================"
echo ""
echo "访问地址："
echo "  EMQX Dashboard:  http://localhost:18083"
echo "  Kibana:          http://localhost:5601"
echo ""
echo "MQTT 连接信息："
echo "  主机: localhost"
echo "  端口: 1883"
echo ""
echo "下一步："
echo "  1. 打开 Dashboard: http://localhost:18083"
echo "  2. 登录: admin / public"
echo "  3. 查看 Overview 页面了解系统状态"
echo "  4. 使用 MQTTX 客户端测试连接"
echo ""
echo "========================================"
