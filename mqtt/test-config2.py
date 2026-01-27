#!/usr/bin/env python3
"""测试配置2"""
import paho.mqtt.client as mqtt
import time

# 配置2: 设备级 Token
MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO&et=1772098636&method=sha1&sign=vzb4PV%2FK%2FvPLSdBd%2FVOVRHrSX44%3D"

print("测试配置2 (设备级 Token)...")
client = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✓ 连接成功!")
    else:
        print(f"✗ 连接失败: {rc}")

client.on_connect = on_connect
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()
time.sleep(2)

success = client.is_connected()
print(f"状态: {'✓ 成功' if success else '✗ 失败'}")

client.disconnect()
client.loop_stop()
