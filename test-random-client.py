#!/usr/bin/env python3
"""
测试使用随机 Client ID 和产品级 Token 订阅消息
"""

import paho.mqtt.client as mqtt
import time

# 配置
MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
PRODUCT_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

# 使用随机 Client ID
CLIENT_ID = f"bridge-{int(time.time())}"

print("="*60)
print("测试随机 Client ID 订阅")
print("="*60)
print(f"Broker: {MQTT_HOST}:{MQTT_PORT}")
print(f"产品ID: {PRODUCT_ID}")
print(f"Client ID: {CLIENT_ID}")
print("="*60)

client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, PRODUCT_TOKEN)

received_count = 0

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n连接结果: {rc}")
    if rc == 0:
        print("✓ 连接成功!")
        # 订阅所有设备消息
        topic = f"$sys/{PRODUCT_ID}/#"
        client.subscribe(topic)
        print(f"已订阅主题: {topic}")
        print("\n等待接收消息... (60秒)")
        print("提示: 请用MQTTX向以下主题发送消息:")
        print(f"  $sys/{PRODUCT_ID}/MO/json")
        print(f"  $sys/{PRODUCT_ID}/MO1/json")
    else:
        print(f"✗ 连接失败,错误码: {rc}")

def on_message(client, userdata, msg):
    global received_count
    received_count += 1
    print(f"\n[{received_count}] 收到消息:")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc, properties=None):
    if rc != 0:
        print(f"\n异常断开: {rc}")

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    # 保持连接 60 秒等待接收消息
    time.sleep(60)

    print(f"\n总共收到 {received_count} 条消息")
    client.disconnect()

except KeyboardInterrupt:
    print("\n\n用户中断")
    client.disconnect()
except Exception as e:
    print(f"\n✗ 异常: {e}")
finally:
    client.loop_stop()
