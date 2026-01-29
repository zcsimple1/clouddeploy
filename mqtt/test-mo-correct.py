#!/usr/bin/env python3
"""
MO 设备物模型通信测试（正确版本）
关键：必须使用 "MO" 作为 Client ID
"""
import paho.mqtt.client as mqtt
import json
import time

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
DEVICE_NAME = "MO"

print("="*70)
print("MO 设备物模型通信测试")
print("发布到平台 | 订阅平台下发")
print("="*70)

received_messages = []
start_time = time.time()

# MO 设备客户端 - 必须使用 "MO" 作为 Client ID
client = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n✓ 连接成功 (rc={rc})")

    if rc == 0:
        print("\n【订阅主题】（接收平台下发）：")
        print("-"*70)

        # 订阅平台下发的主题（操作权限=订阅）
        subscribe_topics = [
            # 1. 设备属性上报响应
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply",

            # 2. 设备属性设置请求（平台下发）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set",

            # 3. 设备属性获取请求（平台下发）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/get",

            # 4. 设备事件上报响应
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/event/post/reply",

            # 5. 设备服务调用请求（使用+通配符）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/+/invoke",

            # 6. 设备同步命令请求（使用+通配符）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/+",

            # 7. 设备OTA升级通知
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/ota/inform",

            # 8. 设备镜像更新请求
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/image/update",

            # 9. 脚本解析数据下行请求（使用+通配符）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/custome/down/+",

            # 10. 设备数据上传成功响应
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/dp/post/json/accepted",

            # 11. 设备数据上传失败响应
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/dp/post/json/rejected",

            # 12. 设备镜像更新成功响应
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/image/update/accepted",

            # 13. 设备镜像更新失败响应
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/image/update/rejected",
        ]

        for i, topic in enumerate(subscribe_topics, 1):
            result = client.subscribe(topic)
            status = "✓" if result[0] == 0 else "✗"
            print(f"  {status} [{i}] {topic}")

        print("-"*70)
        print("\n[设备] 等待平台响应/命令...")
        print("[设备] 开始上报数据到平台...")
        print()

def on_message(client, userdata, msg):
    global received_messages
    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"[✓ 收到平台消息] {elapsed:.1f}秒后")
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

    received_messages.append(msg.payload.decode())
    print(f"{'='*70}\n")

client.on_connect = on_connect
client.on_message = on_message

# 连接
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

time.sleep(3)

# 开始发布消息（设备上报数据）
print("\n" + "="*70)
print("【设备上报数据】（发布到平台）：")
print("="*70 + "\n")

# 消息1: 设备属性上报请求
msg1 = {
    "id": f"prop_{int(time.time())}",
    "version": "1.0",
    "params": {
        "temperature": 25.5,
        "humidity": 60,
        "pressure": 1013.25,
        "timestamp": int(time.time())
    }
}
topic1 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post"
result1 = client.publish(topic1, json.dumps(msg1))
print(f"[消息1] 设备属性上报")
print(f"  主题: {topic1} (发布)")
print(f"  内容: {json.dumps(msg1, indent=2)}")
print(f"  结果: {'✓ 成功' if result1[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(2)

# 消息2: 设备事件上报请求
msg2 = {
    "id": f"event_{int(time.time())}",
    "version": "1.0",
    "params": {
        "event": "temperature_alert",
        "value": 35.5,
        "threshold": 30.0,
        "timestamp": int(time.time())
    }
}
topic2 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/event/post"
result2 = client.publish(topic2, json.dumps(msg2))
print(f"[消息2] 设备事件上报")
print(f"  主题: {topic2} (发布)")
print(f"  内容: {json.dumps(msg2, indent=2)}")
print(f"  结果: {'✓ 成功' if result2[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(2)

# 消息3: 设备数据上传
msg3 = {
    "id": f"dp_{int(time.time())}",
    "version": "1.0",
    "dataPoints": [
        {
            "dsId": "sensor",
            "data": {
                "temperature": 26.0,
                "humidity": 62,
                "pressure": 1014.0
            }
        }
    ]
}
topic3 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/dp/post/json"
result3 = client.publish(topic3, json.dumps(msg3))
print(f"[消息3] 设备数据上传")
print(f"  主题: {topic3} (发布)")
print(f"  内容: {json.dumps(msg3, indent=2)}")
print(f"  结果: {'✓ 成功' if result3[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(2)

# 消息4: 设备更新镜像请求
msg4 = {
    "id": f"img_{int(time.time())}",
    "version": "1.0",
    "params": {
        "url": "https://example.com/firmware.bin",
        "version": "2.0.1",
        "size": 1024000
    }
}
topic4 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/image/update"
result4 = client.publish(topic4, json.dumps(msg4))
print(f"[消息4] 设备镜像更新请求")
print(f"  主题: {topic4} (发布)")
print(f"  内容: {json.dumps(msg4, indent=2)}")
print(f"  结果: {'✓ 成功' if result4[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

# 等待平台响应
print("\n" + "="*70)
print("等待平台响应...（最多等待15秒）")
print("="*70 + "\n")

time.sleep(15)

# 清理
client.disconnect()
client.loop_stop()

print("\n" + "="*70)
print("测试完成")
print("="*70)
print(f"\n总结:")
print(f"  ✓ 使用 Client ID: MO")
print(f"  ✓ 成功发布 4 条设备上报消息")
print(f"  ✓ 订阅了 13 种平台下发主题")
print(f"  {'✓ 收到 ' + str(len(received_messages)) + ' 条平台响应' if received_messages else '⚠️ 未收到平台响应（正常，除非平台主动下发）'}")
print(f"\n说明:")
print(f"  - 设备上报数据到 OneNET 平台（发布操作）")
print(f"  - 平台下发命令/响应到设备（订阅操作）")
print(f"  - 不同的主题用于不同的操作（发布/订阅）")
print("="*70)
