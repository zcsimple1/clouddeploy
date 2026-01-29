#!/usr/bin/env python3
"""发送测试消息到 OneNET MQTT"""
import paho.mqtt.client as mqtt
import json
import time

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

print("="*60)
print("发送测试消息")
print("="*60)

# 使用 MO1 作为 Client ID 发送消息
client = mqtt.Client(client_id="test-sender-123", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, TOKEN)

published = False
def on_connect(client, userdata, flags, rc, properties=None):
    global published
    if rc == 0:
        print("连接成功，发送消息...")
        message = {
            "test": "from-local-python",
            "temp": 25.5,
            "humidity": 60,
            "timestamp": time.time(),
            "device": "test"
        }
        # 尝试发送到不同主题
        topics = [
            f"$sys/{PRODUCT_ID}/test/json",
            f"$sys/{PRODUCT_ID}/MO1/json",
            f"{PRODUCT_ID}/test/data"
        ]

        for topic in topics:
            payload = json.dumps(message)
            result = client.publish(topic, payload)
            print(f"发送到: {topic}")
            print(f"内容: {payload}")
            print(f"结果: {result[0]} {'✓' if result[0] == 0 else '✗'}")
            print()
            published = True
            time.sleep(1)

client.on_connect = on_connect
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

time.sleep(10)

client.disconnect()
client.loop_stop()

if published:
    print("消息发送完成！")
else:
    print("✗ 消息发送失败")
