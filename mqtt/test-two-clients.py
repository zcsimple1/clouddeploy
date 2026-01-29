#!/usr/bin/env python3
"""
使用两个不同连接测试
模拟 MQTTX 的行为：一个客户端订阅，另一个客户端发布
"""
import paho.mqtt.client as mqtt
import json
import time
import threading

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
DEVICE_NAME = "MO"

print("="*70)
print("双连接测试")
print("客户端1: 订阅 | 客户端2: 发布")
print("="*70)

received_messages = []
received_event = threading.Event()
start_time = time.time()

# ==================== 客户端1: 订阅端 ====================
print("\n【启动订阅端】")
sub_client = mqtt.Client(client_id="MO_subscriber", protocol=mqtt.MQTTv311)
sub_client.username_pw_set(PRODUCT_ID, TOKEN)

def sub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"[订阅端] 连接成功 (rc={rc})")
    if rc == 0:
        topics = [
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/+/invoke",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/+",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/dp/post/json/accepted",
        ]
        for topic in topics:
            result = client.subscribe(topic)
            print(f"[订阅端] ✓ 订阅: {topic}")

def sub_on_message(client, userdata, msg):
    global received_messages
    elapsed = time.time() - start_time
    print(f"\n[订阅端 ✓✓✓] 收到消息！ ({elapsed:.1f}秒)")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")
    received_messages.append(msg.payload.decode())
    received_event.set()

sub_client.on_connect = sub_on_connect
sub_client.on_message = sub_on_message
sub_client.connect(MQTT_HOST, MQTT_PORT, 60)
sub_client.loop_start()

time.sleep(2)

# ==================== 客户端2: 发布端 ====================
print("\n【启动发布端】")
pub_client = mqtt.Client(client_id="MO_publisher", protocol=mqtt.MQTTv311)
pub_client.username_pw_set(PRODUCT_ID, TOKEN)

def pub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"[发布端] 连接成功 (rc={rc})")
    if rc == 0:
        print("\n[发布端] 开始发布消息...")

        # 消息1
        msg1 = {"id": "1", "params": {"temp": 25}, "method": "set"}
        topic1 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set"
        result1 = client.publish(topic1, json.dumps(msg1))
        print(f"[发布端 1] {topic1} -> rc={result1[0]}")

        time.sleep(0.5)

        # 消息2
        msg2 = {"id": "2", "code": 200, "msg": "success"}
        topic2 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply"
        result2 = client.publish(topic2, json.dumps(msg2))
        print(f"[发布端 2] {topic2} -> rc={result2[0]}")

        time.sleep(0.5)

        # 消息3
        msg3 = {"cmdId": "cmd123", "params": {"cmd": "reboot"}}
        topic3 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/reboot"
        result3 = client.publish(topic3, json.dumps(msg3))
        print(f"[发布端 3] {topic3} -> rc={result3[0]}")

pub_client.on_connect = pub_on_connect
pub_client.connect(MQTT_HOST, MQTT_PORT, 60)
pub_client.loop_start()

# 等待接收
print("\n" + "="*70)
print("等待订阅端接收消息...（10秒）")
print("="*70 + "\n")

timeout = 10
wait_start = time.time()

while time.time() - wait_start < timeout:
    if received_messages:
        print(f"已收到 {len(received_messages)} 条消息...\n")
        break
    time.sleep(1)

# 清理
sub_client.disconnect()
pub_client.disconnect()
sub_client.loop_stop()
pub_client.loop_stop()

print("\n" + "="*70)
print("测试完成")
print("="*70)
if received_messages:
    print(f"\n✅ 成功！收到 {len(received_messages)} 条消息")
    for i, msg in enumerate(received_messages, 1):
        print(f"  [{i}] {msg[:80]}")
else:
    print("\n❌ 未收到消息")
    print("\n这可能是因为：")
    print("  1. MQTTX 使用了不同的 Token 或 Client ID")
    print("  2. 需要使用 MO1 设备级 Token")
    print("  3. 主题权限限制")
