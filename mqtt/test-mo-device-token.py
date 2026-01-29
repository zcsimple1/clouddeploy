#!/usr/bin/env python3
"""
使用 MO 设备级 Token 测试
验证是否可以发布到订阅主题并接收消息
"""
import paho.mqtt.client as mqtt
import json
import time
import threading

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"

# MO 设备级 Token（不是产品级 Token！）
MO_DEVICE_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO&et=1772098636&method=sha1&sign=vzb4PV%2FK%2FvPLSdBd%2FVOVRHrSX44%3D"
DEVICE_NAME = "MO"

print("="*70)
print("MO 设备级 Token 测试")
print("验证发布到订阅主题是否可行")
print("="*70)

received_messages = []
received_event = threading.Event()
start_time = time.time()

# MO 设备客户端 - 使用设备级 Token
client = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, MO_DEVICE_TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n✓ 连接成功 (rc={rc})")

    if rc == 0:
        print("\n【订阅平台下发的主题】")
        print("-"*70)

        # 订阅平台下发的主题
        topics = [
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/+/invoke",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/+",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/dp/post/json/accepted",
        ]

        for i, topic in enumerate(topics, 1):
            result = client.subscribe(topic)
            status = "✓" if result[0] == 0 else "✗"
            print(f"  {status} [{i}] {topic}")

        print("-"*70)
        print("\n[设备] 等待接收消息...")

def on_message(client, userdata, msg):
    global received_messages
    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"[✓✓✓ 收到消息！] {elapsed:.1f}秒后")
    print(f"{'='*70}")
    print(f"  主题: {msg.topic}")
    print(f"  QoS: {msg.qos} | 保留: {msg.retain}")
    print(f"\n  内容:")

    try:
        payload = msg.payload.decode()
        try:
            json_obj = json.loads(payload)
            print(f"  {json.dumps(json_obj, indent=2, ensure_ascii=False)}")
        except:
            print(f"  {payload}")
    except:
        print(f"  {msg.payload}")

    received_messages.append({
        'topic': msg.topic,
        'payload': msg.payload.decode()
    })
    received_event.set()
    print(f"{'='*70}\n")

def on_publish(client, userdata, mid):
    print(f"[发布] 消息 ID {mid} 已发送")

client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# 连接
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

time.sleep(2)

# 尝试发布到订阅主题
print("\n" + "="*70)
print("【尝试发布到订阅主题】（模拟平台下发）")
print("="*70 + "\n")

# 测试1: 属性设置请求
msg1 = {
    "id": f"set_{int(time.time())}",
    "version": "1.0",
    "params": {
        "temperature": 30.0,
        "humidity": 70
    },
    "method": "thing.service.property.set"
}
topic1 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set"
result1 = client.publish(topic1, json.dumps(msg1))
print(f"[消息1] 属性设置请求")
print(f"  主题: {topic1}")
print(f"  内容: {json.dumps(msg1, indent=2)}")
print(f"  返回码: {result1[0]} {'✓ 成功' if result1[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(1)

# 测试2: 属性上报响应
msg2 = {
    "id": f"prop_{int(time.time())}",
    "code": 200,
    "msg": "success",
    "version": "1.0"
}
topic2 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply"
result2 = client.publish(topic2, json.dumps(msg2))
print(f"[消息2] 属性上报响应")
print(f"  主题: {topic2}")
print(f"  内容: {json.dumps(msg2, indent=2)}")
print(f"  返回码: {result2[0]} {'✓ 成功' if result2[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(1)

# 测试3: 命令下发请求
msg3 = {
    "cmdId": f"cmd_{int(time.time())}",
    "timestamp": int(time.time()),
    "params": {
        "command": "reboot",
        "delay": 5
    }
}
topic3 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/reboot"
result3 = client.publish(topic3, json.dumps(msg3))
print(f"[消息3] 命令下发请求")
print(f"  主题: {topic3}")
print(f"  内容: {json.dumps(msg3, indent=2)}")
print(f"  返回码: {result3[0]} {'✓ 成功' if result3[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

# 等待接收消息
print("\n" + "="*70)
print("等待接收消息...（最多等待10秒）")
print("="*70 + "\n")

timeout = 10
wait_start = time.time()

while time.time() - wait_start < timeout:
    if received_messages:
        print(f"已收到 {len(received_messages)} 条消息，继续等待...\n")
    time.sleep(1)

# 清理
client.disconnect()
client.loop_stop()

print("\n" + "="*70)
print("测试完成")
print("="*70)

if received_messages:
    print(f"\n✅ 成功！使用设备级 Token 可以发布到订阅主题")
    print(f"\n收到的消息：")
    for i, msg in enumerate(received_messages, 1):
        print(f"\n  [{i}] 主题: {msg['topic']}")
        print(f"      内容: {msg['payload'][:100]}..." if len(msg['payload']) > 100 else f"      内容: {msg['payload']}")
else:
    print(f"\n❌ 未收到消息")
    print("\n可能原因：")
    print("  1. OneNET 仍然限制自发自收")
    print("  2. 需要使用不同的 Client ID")
    print("  3. MQTTX 使用了其他配置")

print("\n" + "="*70)
print(f"总结:")
print(f"  Token 类型: 设备级 Token")
print(f"  发布消息: 3 条")
print(f"  订阅主题: 5 个")
print(f"  收到消息: {len(received_messages)} 条")
print("="*70)
