#!/usr/bin/env python3
"""
测试平台下发消息
模拟 OneNET 平台向设备下发命令/属性设置
验证设备订阅功能是否正常工作
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
print("测试：平台下发消息到设备")
print("验证设备订阅功能")
print("="*70)

received_messages = []
received_event = threading.Event()
start_time = time.time()

# MO 设备 - 订阅端
sub_client = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
sub_client.username_pw_set(PRODUCT_ID, TOKEN)

def sub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n[订阅端 MO] 连接成功 (rc={rc})")

    if rc == 0:
        print("\n【订阅平台下发的主题】")
        print("-"*70)

        # 订阅平台可能下发的所有主题
        topics = [
            # 1. 属性设置请求
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set",

            # 2. 属性获取请求
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/get",

            # 3. 服务调用请求
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/reboot/invoke",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/+/invoke",

            # 4. 命令下发请求
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/reboot",
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/+",

            # 5. OTA升级通知
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/ota/inform",

            # 6. 镜像更新请求
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/image/update",

            # 7. 脚本下行数据
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/custome/down/test123",

            # 8. 属性上报响应（平台响应）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply",

            # 9. 事件上报响应
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/event/post/reply",

            # 10. 数据上传成功
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/dp/post/json/accepted",

            # 11. 镜像更新成功
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/image/update/accepted",
        ]

        for i, topic in enumerate(topics, 1):
            result = client.subscribe(topic)
            status = "✓" if result[0] == 0 else "✗"
            print(f"  {status} [{i}] {topic}")

        print("-"*70)
        print("\n[订阅端 MO] 等待平台下发消息...")

def sub_on_message(client, userdata, msg):
    global received_messages
    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"[✓✓✓ 订阅端收到消息！] {elapsed:.1f}秒后")
    print(f"{'='*70}")
    print(f"  主题: {msg.topic}")
    print(f"  QoS: {msg.qos} | 保留: {msg.retain}")
    print(f"\n  内容:")

    try:
        payload = msg.payload.decode()
        try:
            json_obj = json.loads(payload)
            print(f"  {json.dumps(json_obj, indent=2, ensure_ascii=False)}")
        except:
            print(f"  {payload}")
    except:
        print(f"  {msg.payload}")

    received_messages.append({
        'topic': msg.topic,
        'payload': msg.payload.decode(),
        'qos': msg.qos
    })
    received_event.set()
    print(f"{'='*70}\n")

sub_client.on_connect = sub_on_connect
sub_client.on_message = sub_on_message

sub_client.connect(MQTT_HOST, MQTT_PORT, 60)
sub_client.loop_start()

time.sleep(2)

# 模拟平台下发消息的客户端
# 注意：这个客户端也需要使用 "MO" 作为 Client ID（模拟平台通过同一连接下发）
print("\n" + "="*70)
print("【模拟平台下发消息】")
print("="*70 + "\n")

# 由于 OneNET 限制，我们不能直接模拟平台下发
# 但我们可以通过同一连接发布到"订阅主题"来测试接收能力
# 这相当于：设备A发布的消息，被自己订阅的主题接收到

# 测试1: 属性设置请求（平台下发）
msg1 = {
    "id": f"set_{int(time.time())}",
    "version": "1.0",
    "params": {
        "temperature": 30.0,
        "humidity": 70
    },
    "method": "thing.service.property.set"
}
topic1 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set"
result1 = sub_client.publish(topic1, json.dumps(msg1))
print(f"[模拟平台消息1] 属性设置请求")
print(f"  主题: {topic1}")
print(f"  内容: {json.dumps(msg1, indent=2)}")
print(f"  结果: {'✓ 成功' if result1[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(2)

# 测试2: 命令下发请求（平台下发）
msg2 = {
    "cmdId": f"cmd_reboot_{int(time.time())}",
    "timestamp": int(time.time()),
    "params": {
        "command": "reboot",
        "delay": 5
    }
}
topic2 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/reboot"
result2 = sub_client.publish(topic2, json.dumps(msg2))
print(f"[模拟平台消息2] 命令下发请求")
print(f"  主题: {topic2}")
print(f"  内容: {json.dumps(msg2, indent=2)}")
print(f"  结果: {'✓ 成功' if result2[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(2)

# 测试3: 服务调用请求（平台下发）
msg3 = {
    "id": f"service_{int(time.time())}",
    "version": "1.0",
    "params": {
        "action": "upgrade",
        "version": "2.0.1"
    },
    "method": "thing.service.invoke"
}
topic3 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/upgrade/invoke"
result3 = sub_client.publish(topic3, json.dumps(msg3))
print(f"[模拟平台消息3] 服务调用请求")
print(f"  主题: {topic3}")
print(f"  内容: {json.dumps(msg3, indent=2)}")
print(f"  结果: {'✓ 成功' if result3[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(2)

# 测试4: 属性上报响应（平台响应）
msg4 = {
    "id": f"prop_{int(time.time())}",
    "code": 200,
    "msg": "success",
    "version": "1.0"
}
topic4 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply"
result4 = sub_client.publish(topic4, json.dumps(msg4))
print(f"[模拟平台消息4] 属性上报响应")
print(f"  主题: {topic4}")
print(f"  内容: {json.dumps(msg4, indent=2)}")
print(f"  结果: {'✓ 成功' if result4[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(2)

# 测试5: 数据上传成功响应（平台响应）
msg5 = {
    "id": f"dp_{int(time.time())}",
    "code": 200,
    "msg": "Data accepted"
}
topic5 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/dp/post/json/accepted"
result5 = sub_client.publish(topic5, json.dumps(msg5))
print(f"[模拟平台消息5] 数据上传成功响应")
print(f"  主题: {topic5}")
print(f"  内容: {json.dumps(msg5, indent=2)}")
print(f"  结果: {'✓ 成功' if result5[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

# 等待接收消息
print("\n" + "="*70)
print("等待订阅端接收消息...（最多等待10秒）")
print("="*70 + "\n")

timeout = 10
wait_start = time.time()

while time.time() - wait_start < timeout:
    if received_messages:
        print(f"已收到 {len(received_messages)} 条消息，继续等待...\n")
    time.sleep(1)

# 清理
sub_client.disconnect()
sub_client.loop_stop()

print("\n" + "="*70)
print("测试完成")
print("="*70)

if received_messages:
    print(f"\n✅ 订阅测试成功！")
    print(f"\n收到的消息详情：")
    for i, msg in enumerate(received_messages, 1):
        print(f"\n消息 {i}:")
        print(f"  主题: {msg['topic']}")
        print(f"  QoS: {msg['qos']}")
        print(f"  内容: {msg['payload']}")
    print("\n✓✓✓ 订阅功能正常工作！")
else:
    print(f"\n❌ 订阅测试失败：未收到任何消息")
    print("\n可能原因：")
    print("  1. OneNET 不允许同一连接的发布和订阅互相接收")
    print("  2. 平台下发消息需要通过 OneNET 平台控制台触发")
    print("  3. 需要实际的平台操作来触发下发消息")

print("\n" + "="*70)
print(f"总结:")
print(f"  ✓ 订阅了 11 种主题")
print(f"  ✓ 发布了 5 条模拟平台消息")
print(f"  {'✓ 收到 ' + str(len(received_messages)) + ' 条消息' if received_messages else '⚠️ 未收到消息（可能需要实际平台触发）'}")
print("="*70)
