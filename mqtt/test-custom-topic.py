#!/usr/bin/env python3
"""测试自定义主题的订阅和发送"""
import paho.mqtt.client as mqtt
import json
import time
import threading

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

print("="*60)
print("测试自定义主题")
print("="*60)

received_messages = []
received_event = threading.Event()

# 订阅端 - 使用 MO，订阅自定义主题
sub_client = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
sub_client.username_pw_set(PRODUCT_ID, TOKEN)

def sub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n[订阅端] 连接结果: {rc}")
    if rc == 0:
        # 订阅自定义主题
        topic = f"{PRODUCT_ID}/#"
        client.subscribe(topic)
        print(f"[订阅端] ✓ 订阅成功: {topic}")
        print("[订阅端] 等待接收消息...")
    else:
        print(f"[订阅端] ✗ 订阅失败: {rc}")

def sub_on_message(client, userdata, msg):
    print(f"\n[订阅端] ✓✓✓ 收到消息! ✓✓✓")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")
    received_messages.append(msg.payload.decode())
    received_event.set()

sub_client.on_connect = sub_on_connect
sub_client.on_message = sub_on_message

sub_client.connect(MQTT_HOST, MQTT_PORT, 60)
sub_client.loop_start()

time.sleep(2)

# 发送端 - 使用 MO1
print("\n" + "="*60)
print("开始发送到自定义主题...")
print("="*60 + "\n")

pub_client = mqtt.Client(client_id="MO1", protocol=mqtt.MQTTv311)
MO1_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772105871&method=sha1&sign=ZZoc17%2BbrxprIZ7prgo82Y%2FTDG4%3D"
pub_client.username_pw_set(PRODUCT_ID, MO1_TOKEN)

def pub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"[发送端] 连接结果: {rc}")
    if rc == 0:
        message = {
            "test": "custom-topic-test",
            "temp": 25.5,
            "humidity": 60,
            "timestamp": time.time(),
            "device": "MO1"
        }

        # 发送到自定义主题
        topic = f"{PRODUCT_ID}/MO1/data"
        payload = json.dumps(message)
        result = client.publish(topic, payload)
        print(f"[发送端] 发送到: {topic}")
        print(f"[发送端] 内容: {payload}")
        print(f"[发送端] 结果: {result[0]} {'✓ 成功' if result[0] == 0 else '✗ 失败'}\n")

pub_client.on_connect = pub_on_connect
pub_client.connect(MQTT_HOST, MQTT_PORT, 60)
pub_client.loop_start()

# 等待接收消息
print("="*60)
print("等待接收消息（最多等待10秒）...")
print("="*60 + "\n")

if received_event.wait(timeout=10):
    print("\n✓✓✓ 成功！订阅端收到了消息 ✓✓✓")
    success = True
else:
    print("\n✗ 未收到消息")
    success = False

# 清理
sub_client.disconnect()
pub_client.disconnect()
sub_client.loop_stop()
pub_client.loop_stop()

print("\n" + "="*60)
if success:
    print("✅ 自定义主题测试成功！")
    print("ESP32 应该发送到自定义主题，而不是 $sys 主题")
else:
    print("❌ 自定义主题测试失败")
print("="*60)
