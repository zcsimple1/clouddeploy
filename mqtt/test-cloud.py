#!/usr/bin/env python3
"""云服务器 MQTT 连接测试脚本"""
import paho.mqtt.client as mqtt
import json
import time
import threading

# 使用产品级 Token
MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

print("="*60)
print("云服务器 MQTT 环境测试")
print("="*60)
print(f"Broker: {MQTT_HOST}:{MQTT_PORT}")
print(f"Product ID: {PRODUCT_ID}")
print("="*60)
print()

# 测试1: 连接测试
print("\n测试1: 连接测试 (随机 Client ID)")
print("-"*60)
client1 = mqtt.Client(client_id="cloud-test-" + str(int(time.time())), protocol=mqtt.MQTTv311)
client1.username_pw_set(PRODUCT_ID, TOKEN)

connected = False
def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"✓ 连接成功! (rc={rc})")
    else:
        print(f"✗ 连接失败 (rc={rc})")

client1.on_connect = on_connect
client1.connect(MQTT_HOST, MQTT_PORT, 60)
client1.loop_start()
time.sleep(3)
client1.disconnect()
client1.loop_stop()
test1_result = connected
print(f"结果: {'✓ 通过' if test1_result else '✗ 失败'}")

# 测试2: 订阅测试
print("\n测试2: 订阅测试")
print("-"*60)
client2 = mqtt.Client(client_id="cloud-sub-" + str(int(time.time())), protocol=mqtt.MQTTv311)
client2.username_pw_set(PRODUCT_ID, TOKEN)

subscribed = False
def sub_on_connect(client, userdata, flags, rc, properties=None):
    global subscribed
    if rc == 0:
        topic = f"$sys/{PRODUCT_ID}/#"
        client.subscribe(topic)
        print(f"✓ 订阅成功: {topic}")
        subscribed = True
    else:
        print(f"✗ 订阅失败 (rc={rc})")

def sub_on_message(client, userdata, msg):
    print(f"  收到消息: {msg.topic} - {msg.payload.decode()}")

client2.on_connect = sub_on_connect
client2.on_message = sub_on_message
client2.connect(MQTT_HOST, MQTT_PORT, 60)
client2.loop_start()
time.sleep(3)
client2.disconnect()
client2.loop_stop()
test2_result = subscribed
print(f"结果: {'✓ 通过' if test2_result else '✗ 失败'}")

# 测试3: 发布测试
print("\n测试3: 发布测试")
print("-"*60)
client3 = mqtt.Client(client_id="cloud-pub-" + str(int(time.time())), protocol=mqtt.MQTTv311)
client3.username_pw_set(PRODUCT_ID, TOKEN)

published = False
def pub_on_connect(client, userdata, flags, rc, properties=None):
    global published
    if rc == 0:
        message = {"test": "cloud-server", "timestamp": time.time()}
        topic = f"$sys/{PRODUCT_ID}/test/json"
        payload = json.dumps(message)
        result = client.publish(topic, payload)
        if result[0] == 0:
            published = True
            print(f"✓ 发布成功: {topic}")
            print(f"  内容: {payload}")
        else:
            print(f"✗ 发布失败 (rc={result[0]})")
    else:
        print(f"✗ 连接失败 (rc={rc})")

client3.on_connect = pub_on_connect
client3.connect(MQTT_HOST, MQTT_PORT, 60)
client3.loop_start()
time.sleep(3)
client3.disconnect()
client3.loop_stop()
test3_result = published
print(f"结果: {'✓ 通过' if test3_result else '✗ 失败'}")

# 测试4: 使用 MO 作为 Client ID
print("\n测试4: 使用 MO 作为 Client ID")
print("-"*60)
client4 = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
client4.username_pw_set(PRODUCT_ID, TOKEN)

mo_connected = False
def mo_on_connect(client, userdata, flags, rc, properties=None):
    global mo_connected
    if rc == 0:
        mo_connected = True
        topic = f"$sys/{PRODUCT_ID}/#"
        client.subscribe(topic)
        print(f"✓ MO 连接并订阅成功: {topic}")
    else:
        print(f"✗ MO 连接失败 (rc={rc})")
        if rc == 4:
            print("  提示: MO 可能已被其他客户端占用")

client4.on_connect = mo_on_connect
client4.connect(MQTT_HOST, MQTT_PORT, 60)
client4.loop_start()
time.sleep(3)
client4.disconnect()
client4.loop_stop()
test4_result = mo_connected
print(f"结果: {'✓ 通过' if test4_result else '✗ 失败'}")

# 总结
print("\n" + "="*60)
print("测试总结")
print("="*60)
print(f"测试1 - 连接测试:         {'✓ 通过' if test1_result else '✗ 失败'}")
print(f"测试2 - 订阅测试:         {'✓ 通过' if test2_result else '✗ 失败'}")
print(f"测试3 - 发布测试:         {'✓ 通过' if test3_result else '✗ 失败'}")
print(f"测试4 - MO Client ID:     {'✓ 通过' if test4_result else '✗ 失败'}")
print("="*60)

if all([test1_result, test2_result, test3_result]):
    print("\n✅ 云服务器 MQTT 环境测试通过!")
    print("   可以正常使用 MQTT 连接 OneNET 平台")
elif test4_result:
    print("\n✅ MO 设备连接正常，但随机 Client ID 测试失败")
    print("   建议: 使用 MO 作为 Client ID 进行连接")
else:
    print("\n❌ 测试失败，请检查:")
    print("   1. 网络连接 (ping mqtts.heclouds.com)")
    print("   2. Token 是否过期")
    print("   3. 防火墙设置")
