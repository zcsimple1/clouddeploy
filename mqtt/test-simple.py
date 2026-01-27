#!/usr/bin/env python3
"""
简单测试: 使用配置1连接、订阅、发布
"""

import paho.mqtt.client as mqtt
import json
import time
import threading

# 配置1: 产品级 Token
MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

print("="*60)
print("测试1: 连接测试 (随机Client ID)")
print("="*60)

client1 = mqtt.Client(client_id="test-bridge-123", protocol=mqtt.MQTTv311)
client1.username_pw_set(PRODUCT_ID, TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"连接结果: {rc} {'✓ 成功' if rc == 0 else '✗ 失败'}")

client1.on_connect = on_connect
client1.connect(MQTT_HOST, MQTT_PORT, 60)
client1.loop_start()
time.sleep(3)
result1 = client1.is_connected()
client1.disconnect()
client1.loop_stop()

print(f"结果: {'✓ 通过' if result1 else '✗ 失败'}")

print("\n" + "="*60)
print("测试2: 发布消息")
print("="*60)

client2 = mqtt.Client(client_id="test-pub-MO1", protocol=mqtt.MQTTv311)
client2.username_pw_set(PRODUCT_ID, TOKEN)

def pub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"连接结果: {rc}")
    if rc == 0:
        message = {"temp": 25.5, "device": "test-python", "time": time.time()}
        topic = f"$sys/{PRODUCT_ID}/MO1/json"
        payload = json.dumps(message)
        print(f"发布到: {topic}")
        print(f"内容: {payload}")
        result = client.publish(topic, payload)
        print(f"发布结果: {result[0]} {'✓ 成功' if result[0] == 0 else '✗ 失败'}")

client2.on_connect = pub_on_connect
client2.connect(MQTT_HOST, MQTT_PORT, 60)
client2.loop_start()
time.sleep(3)
result2 = client2.is_connected()
client2.disconnect()
client2.loop_stop()

print(f"结果: {'✓ 通过' if result2 else '✗ 失败'}")

print("\n" + "="*60)
print("测试3: 订阅消息 (等待5秒)")
print("="*60)

received = threading.Event()
received_msg = {}

client3 = mqtt.Client(client_id="test-sub-bridge", protocol=mqtt.MQTTv311)
client3.username_pw_set(PRODUCT_ID, TOKEN)

def sub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"连接结果: {rc}")
    if rc == 0:
        topic = f"$sys/{PRODUCT_ID}/#"
        client.subscribe(topic)
        print(f"订阅: {topic}")
        print("等待消息... (你可以在MQTTX发送消息测试)")

def sub_on_message(client, userdata, msg):
    print(f"\n✓ 收到消息!")
    print(f"主题: {msg.topic}")
    print(f"内容: {msg.payload.decode()}")
    received_msg['data'] = msg.payload.decode()
    received.set()

client3.on_connect = sub_on_connect
client3.on_message = sub_on_message

client3.connect(MQTT_HOST, MQTT_PORT, 60)
client3.loop_start()
time.sleep(5)

if received.is_set():
    print("\n✓ 测试3: 通过 (收到消息)")
    result3 = True
else:
    print("\n⚠ 测试3: 未收到消息 (可能需要MQTTX发送)")
    result3 = None

client3.disconnect()
client3.loop_stop()

print("\n" + "="*60)
print("测试总结:")
print("="*60)
print(f"连接测试: {'✓ 通过' if result1 else '✗ 失败'}")
print(f"发布测试: {'✓ 通过' if result2 else '✗ 失败'}")
print(f"订阅测试: {'✓ 通过' if result3 else '⚠ 等待MQTTX发送'}")
print("="*60)
