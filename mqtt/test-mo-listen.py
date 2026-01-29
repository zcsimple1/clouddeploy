#!/usr/bin/env python3
"""
测试 MO 设备接收 OneNET 平台消息
监听一段时间，看能否接收到任何消息
"""
import paho.mqtt.client as mqtt
import json
import time
import signal
import sys

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

received_count = 0
start_time = time.time()

# 全局客户端
client = mqtt.Client(client_id="MO_test_subscribe", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n✓ 连接成功 (rc={rc})")

    if rc == 0:
        print("\n订阅的主题模式：")
        print("="*70)

        # 订阅所有可能的 OneNET 主题
        topics = [
            # 方式1: 全部物模型相关
            f"$sys/{PRODUCT_ID}/MO/thing/#",

            # 方式2: 物模型属性类
            f"$sys/{PRODUCT_ID}/MO/thing/property/#",

            # 方式3: 物模型服务调用（使用+通配符）
            f"$sys/{PRODUCT_ID}/MO/thing/service/+/invoke",
            f"$sys/{PRODUCT_ID}/MO/thing/service/+/invoke_reply",

            # 方式4: 数据流命令下发
            f"$sys/{PRODUCT_ID}/MO/cmd/#",
            f"$sys/{PRODUCT_ID}/MO/cmd/request/+",
            f"$sys/{PRODUCT_ID}/MO/cmd/response/+/accepted",
            f"$sys/{PRODUCT_ID}/MO/cmd/response/+/rejected",

            # 方式5: 订阅所有设备的消息（测试）
            f"$sys/{PRODUCT_ID}/#",
        ]

        for i, topic in enumerate(topics, 1):
            result = client.subscribe(topic)
            status = "✓" if result[0] == 0 else "✗"
            print(f"  {status} [{i}] {topic} (QoS={result[1]})")

        print("="*70)
        print("\n监听中... (等待接收 OneNET 平台消息)")
        print("按 Ctrl+C 退出\n")

def on_message(client, userdata, msg):
    global received_count
    received_count += 1
    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"[消息 #{received_count}] 收到于 {elapsed:.1f} 秒后")
    print(f"{'='*70}")
    print(f"  主题: {msg.topic}")
    print(f"  QoS: {msg.qos} | 保留: {msg.retain}")
    print(f"  大小: {len(msg.payload)} 字节")
    print(f"\n  内容:")

    try:
        payload = msg.payload.decode()
        # 尝试格式化 JSON
        try:
            json_obj = json.loads(payload)
            print(f"  {json.dumps(json_obj, indent=2, ensure_ascii=False)}")
        except:
            print(f"  {payload}")
    except:
        print(f"  {msg.payload}")

    print(f"{'='*70}\n")

def on_disconnect(client, userdata, rc):
    print(f"\n✗ 连接断开 (rc={rc})")
    if rc != 0:
        print("5秒后尝试重新连接...")
        time.sleep(5)
        try:
            client.reconnect()
        except:
            pass

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

def signal_handler(sig, frame):
    print("\n\n用户中断，停止监听...")
    print(f"\n监听统计:")
    print(f"  运行时间: {time.time() - start_time:.1f} 秒")
    print(f"  收到消息: {received_count} 条")
    client.disconnect()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    print(f"\n{'='*70}")
    print("MO 设备订阅测试 - 监听 OneNET 平台消息")
    print(f"{'='*70}")
    print(f"\n连接信息:")
    print(f"  Broker: {MQTT_HOST}:{MQTT_PORT}")
    print(f"  Client ID: MO_test_subscribe")
    print(f"  Product ID: {PRODUCT_ID}")
    print(f"  Token: 产品级 Token")

    client.connect(MQTT_HOST, MQTT_PORT, 60)

    print("\n开始循环...")
    print("提示：可以在 OneNET 平台触发以下操作来测试：")
    print("  - 设备属性上报（通过其他方式）")
    print("  - 平台下发命令到 MO 设备")
    print("  - 物模型服务调用")
    print("="*70 + "\n")

    client.loop_forever()

except KeyboardInterrupt:
    signal_handler(None, None)

except Exception as e:
    print(f"\n错误: {e}")
    client.disconnect()
