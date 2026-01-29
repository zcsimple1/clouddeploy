#!/usr/bin/env python3
"""
MO 设备主题订阅测试
使用 MO 设备订阅各种主题格式，验证接收能力
"""
import paho.mqtt.client as mqtt
import json
import time

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

print("="*70)
print("MO 设备主题订阅测试")
print("="*70)

received_count = 0
start_time = time.time()

# 订阅客户端
client = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n✓ 连接成功 (rc={rc})")

    if rc == 0:
        print("\n订阅的主题模式：")
        print("-"*70)

        # 订阅所有OneNET标准主题
        topics = [
            # 1. 订阅全部物模型相关主题：# 多层通配符
            f"$sys/{PRODUCT_ID}/MO/thing/#",

            # 2. 订阅物模型属性类相关主题
            f"$sys/{PRODUCT_ID}/MO/thing/property/#",

            # 3. 订阅物模型服务调用类相关主题（使用+单层通配符）
            f"$sys/{PRODUCT_ID}/MO/thing/service/+/invoke",
            f"$sys/{PRODUCT_ID}/MO/thing/service/+/invoke_reply",

            # 4. 订阅数据流模式下的命令下发
            f"$sys/{PRODUCT_ID}/MO/cmd/#",
            f"$sys/{PRODUCT_ID}/MO/cmd/request/+",
            f"$sys/{PRODUCT_ID}/MO/cmd/response/+/accepted",
            f"$sys/{PRODUCT_ID}/MO/cmd/response/+/rejected",
        ]

        for i, topic in enumerate(topics, 1):
            result = client.subscribe(topic)
            status = "✓" if result[0] == 0 else "✗"
            print(f"  {status} [{i}] {topic} (QoS={result[1]})")

        print("-"*70)
        print("\n等待接收消息...（按 Ctrl+C 退出）\n")
        print("="*70)

def on_message(client, userdata, msg):
    global received_count
    received_count += 1
    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"[消息 #{received_count}] 收到于 {elapsed:.1f} 秒后")
    print(f"{'='*70}")
    print(f"  主题: {msg.topic}")
    print(f"  QoS: {msg.qos} | 保留: {msg.retain}")
    print(f"  长度: {len(msg.payload)} 字节")
    print(f"\n  内容:")
    print(f"  {msg.payload.decode()}")
    print(f"{'='*70}\n")

def on_disconnect(client, userdata, rc):
    print(f"\n✗ 连接断开 (rc={rc})")
    if rc != 0:
        print("尝试重新连接...")

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

print(f"\n连接信息:")
print(f"  Broker: {MQTT_HOST}:{MQTT_PORT}")
print(f"  Client ID: MO")
print(f"  Product ID: {PRODUCT_ID}")

try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("\n\n用户中断，退出测试...")
    print(f"\n测试统计:")
    print(f"  运行时间: {time.time() - start_time:.1f} 秒")
    print(f"  收到消息: {received_count} 条")

except Exception as e:
    print(f"\n错误: {e}")

finally:
    client.disconnect()
    print("\n测试结束")
