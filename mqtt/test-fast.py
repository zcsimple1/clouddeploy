#!/usr/bin/env python3
"""快速连接测试"""
import paho.mqtt.client as mqtt
import time

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

print("="*50)
print("快速 MQTT 连接测试")
print("="*50)

client = mqtt.Client(client_id="fast-test-" + str(int(time.time())), protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, TOKEN)

connected = False
def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    print(f"连接结果: {rc}")
    if rc == 0:
        print("✓ 连接成功!")
        connected = True
    else:
        print(f"✗ 连接失败: {rc}")

client.on_connect = on_connect
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

time.sleep(2)

client.disconnect()
client.loop_stop()

print("="*50)
print(f"最终状态: {'✓ 成功' if connected else '✗ 失败'}")
print("="*50)
