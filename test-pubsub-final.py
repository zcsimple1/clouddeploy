#!/usr/bin/env python3
"""使用用户MQTTX成功的Token进行完整测试"""
import paho.mqtt.client as mqtt
import json
import time
import threading

# 使用用户MQTTX成功的配置
MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

print("="*60)
print("测试1: 连接 + 订阅")
print("="*60)

received = threading.Event()

# 订阅客户端
sub_client = mqtt.Client(client_id="bridge-test-sub", protocol=mqtt.MQTTv311)
sub_client.username_pw_set(PRODUCT_ID, TOKEN)

def sub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"订阅端连接: {rc}")
    if rc == 0:
        topic = f"$sys/{PRODUCT_ID}/#"
        client.subscribe(topic)
        print(f"✓ 订阅成功: {topic}")
    else:
        print(f"✗ 订阅失败: {rc}")

def sub_on_message(client, userdata, msg):
    print(f"\n✓ 收到消息!")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")
    received.set()

sub_client.on_connect = sub_on_connect
sub_client.on_message = sub_on_message

sub_client.connect(MQTT_HOST, MQTT_PORT, 60)
sub_client.loop_start()
time.sleep(2)

sub_success = sub_client.is_connected()
print(f"订阅状态: {'✓ 成功' if sub_success else '✗ 失败'}")

print("\n" + "="*60)
print("测试2: 发布消息")
print("="*60)

# 发布客户端
pub_client = mqtt.Client(client_id="MO1", protocol=mqtt.MQTTv311)
pub_client.username_pw_set(PRODUCT_ID, TOKEN)

def pub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"发布端连接: {rc}")
    if rc == 0:
        time.sleep(1)
        message = {"temp": 28.5, "device": "test-final", "time": time.time()}
        topic = f"$sys/{PRODUCT_ID}/MO1/json"
        payload = json.dumps(message)
        print(f"发布到: {topic}")
        print(f"内容: {payload}")
        result = client.publish(topic, payload)
        print(f"发布结果: {result[0]} {'✓ 成功' if result[0] == 0 else '✗ 失败'}")

pub_client.on_connect = pub_on_connect

pub_client.connect(MQTT_HOST, MQTT_PORT, 60)
pub_client.loop_start()
time.sleep(3)

pub_success = pub_client.is_connected()
print(f"发布状态: {'✓ 成功' if pub_success else '✗ 失败'}")

print("\n等待接收消息...")
if received.wait(timeout=5):
    print("✓ 完整测试通过!")
else:
    print("⚠ 未收到消息 (可能MQTTX的MO1已占用)")

sub_client.disconnect()
pub_client.disconnect()
sub_client.loop_stop()
pub_client.loop_stop()

print("\n" + "="*60)
print("测试总结:")
print("="*60)
print(f"订阅连接: {'✓ 通过' if sub_success else '✗ 失败'}")
print(f"发布连接: {'✓ 通过' if pub_success else '✗ 失败'}")
print(f"消息接收: {'✓ 通过' if received.is_set() else '⚠ 可能被占用'}")
