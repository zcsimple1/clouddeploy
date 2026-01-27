#!/usr/bin/env python3
"""验证使用MO作为Client ID的连接和订阅"""
import paho.mqtt.client as mqtt
import json
import time

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

print("="*60)
print("验证: 使用MO作为Client ID连接并订阅")
print("="*60)

client = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"连接结果: {rc}")
    if rc == 0:
        print("✓ 连接成功!")
        topic = f"$sys/{PRODUCT_ID}/#"
        client.subscribe(topic)
        print(f"✓ 订阅成功: {topic}")
        print("\n等待消息... (15秒,请在MQTTX发送测试消息)")
    else:
        print(f"✗ 连接失败: {rc}")
        if rc == 4:
            print("  提示: 可能MO被MQTTX或其他客户端占用")
            print("  解决: 断开MQTTX的MO连接后重试")

def on_message(client, userdata, msg):
    print(f"\n✓ 收到消息!")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

time.sleep(15)

print("\n测试结束")
client.disconnect()
client.loop_stop()
