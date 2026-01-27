#!/bin/bash

# MQTT 桥接服务诊断脚本

echo "================================"
echo "MQTT 桥接服务诊断"
echo "================================"
echo ""

# 1. 检查 mosquitto-clients
echo "1. 检查 mosquitto-clients..."
if command -v mosquitto_sub &> /dev/null; then
    echo "✓ mosquitto-clients 已安装: $(mosquitto_sub --help | head -n1)"
else
    echo "✗ mosquitto-clients 未安装"
    echo "  安装命令: apt-get install -y mosquitto-clients"
fi
echo ""

# 2. 检查 elk-mqtt 服务
echo "2. 检查 elk-mqtt 服务状态..."
if systemctl list-unit-files | grep -q elk-mqtt; then
    STATUS=$(systemctl is-active elk-mqtt 2>/dev/null)
    if [ "$STATUS" = "active" ]; then
        echo "✓ elk-mqtt 服务运行中"
    else
        echo "✗ elk-mqtt 服务状态: $STATUS"
        echo "  启动命令: sudo systemctl start elk-mqtt"
    fi
else
    echo "✗ elk-mqtt 服务未安装"
    echo "  安装命令: bash setup-mqtt.sh"
fi
echo ""

# 3. 检查 Logstash HTTP 端口
echo "3. 检查 Logstash HTTP 端口 (5000)..."
if command -v curl &> /dev/null; then
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        echo "✓ Logstash HTTP 端口 (5000) 可访问"
    else
        echo "✗ Logstash HTTP 端口 (5000) 不可访问"
        echo "  检查命令: docker ps | grep logstash"
        echo "  查看日志: docker logs logstash"
    fi
else
    echo "⚠ curl 未安装，无法测试端口"
fi
echo ""

# 4. 检查 elk-mqtt 日志
echo "4. elk-mqtt 服务日志（最近20行）:"
if systemctl list-unit-files | grep -q elk-mqtt; then
    journalctl -u elk-mqtt -n 20 --no-pager 2>/dev/null || echo "  无法读取日志"
else
    echo "  服务未安装"
fi
echo ""

# 5. 测试 MQTT 连接
echo "5. 测试 MQTT 连接（快速测试）..."
if command -v mosquitto_sub &> /dev/null; then
    echo "尝试连接到 OneNET MQTT..."
    timeout 3 mosquitto_sub -h mqtts.heclouds.com -p 1883 \
        -u v6IkuqD6vh \
        -P "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D" \
        -i test-diagnose-$$ \
        -t "\$sys/v6IkuqD6vh/#" \
        -v -C 1 2>&1 || echo "  连接测试超时或失败（预期行为，3秒后自动退出）"
    echo "  如果看到 '连接成功'，说明 MQTT 连接正常"
else
    echo "⚠ mosquitto-clients 未安装，跳过连接测试"
fi
echo ""

echo "================================"
echo "诊断完成"
echo "================================"
echo ""
