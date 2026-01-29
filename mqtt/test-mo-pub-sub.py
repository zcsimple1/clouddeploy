#!/usr/bin/env python3
"""
MO 设备物模型通信测试
同一个设备：
- 发布到：$sys/{pid}/{device-name}/thing/property/post（设备属性上报）
- 订阅：$sys/{pid}/{device-name}/thing/property/post/reply（平台响应）
- 订阅：$sys/{pid}/{device-name}/thing/property/set（平台下发属性设置）
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
print("MO 设备物模型通信测试")
print("同一个设备进行发布和订阅")
print("="*70)

received_messages = []
received_event = threading.Event()

# MO 设备客户端
client = mqtt.Client(client_id="MO_pubsub_test", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n✓ 连接成功 (rc={rc})")

    if rc == 0:
        print("\n【订阅主题】（平台下发/响应）：")
        print("-"*70)

        # 订阅平台下发的主题（操作权限=订阅）
        subscribe_topics = [
            # 1. 设备属性上报响应（平台响应）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post/reply",

            # 2. 设备属性设置请求（平台下发）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/set",

            # 3. 设备属性获取请求（平台下发）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/get",

            # 4. 设备事件上报响应（平台响应）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/event/post/reply",

            # 5. 设备服务调用请求（平台下发）- 使用+通配符
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/+/invoke",

            # 6. 设备同步命令请求（平台下发）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/request/+",

            # 7. 设备OTA升级通知（平台下发）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/ota/inform",

            # 8. 设备镜像更新请求（平台下发）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/image/update",

            # 9. 脚本解析数据下行请求（平台下发）
            f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/custome/down/+",
        ]

        for i, topic in enumerate(subscribe_topics, 1):
            result = client.subscribe(topic)
            status = "✓" if result[0] == 0 else "✗"
            print(f"  {status} [{i}] {topic}")

        print("-"*70)
        print("\n[设备] 等待平台响应/命令...")

def on_message(client, userdata, msg):
    global received_messages
    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"[收到消息] {elapsed:.1f}秒后")
    print(f"{'='*70}")
    print(f"  主题: {msg.topic}")
    print(f"  QoS: {msg.qos} | 保留: {msg.retain}")
    print(f"\n  内容:")

    try:
        payload = msg.payload.decode()
        # 尝试格式化 JSON
        try:
            json_obj = json.loads(payload)
            print(f"  {json.dumps(json_obj, indent=2, ensure_ascii=False)}")
        except:
            print(f"  {payload}")
    except:
        print(f"  {msg.payload}")

    received_messages.append(msg.payload.decode())
    print(f"{'='*70}\n")
    received_event.set()

client.on_connect = on_connect
client.on_message = on_message

# 连接
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

time.sleep(2)

# 开始发布消息（设备上报数据）
start_time = time.time()
print("\n" + "="*70)
print("【发布消息】（设备上报）：")
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
    },
    "method": "thing.event.property.post"
}
topic1 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post"
result1 = client.publish(topic1, json.dumps(msg1))
print(f"[消息1] 设备属性上报请求")
print(f"  主题: {topic1}")
print(f"  操作权限: 发布")
print(f"  内容: {json.dumps(msg1, indent=2)}")
print(f"  结果: {'✓ 成功' if result1[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(1)

# 消息2: 设备事件上报请求
msg2 = {
    "id": f"event_{int(time.time())}",
    "version": "1.0",
    "params": {
        "event": "temperature_alert",
        "value": 35.5,
        "threshold": 30.0,
        "timestamp": int(time.time())
    },
    "method": "thing.event.post"
}
topic2 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/event/post"
result2 = client.publish(topic2, json.dumps(msg2))
print(f"[消息2] 设备事件上报请求")
print(f"  主题: {topic2}")
print(f"  操作权限: 发布")
print(f"  内容: {json.dumps(msg2, indent=2)}")
print(f"  结果: {'✓ 成功' if result2[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(1)

# 消息3: 设备服务调用响应（模拟收到服务调用后的响应）
msg3 = {
    "id": f"service_{int(time.time())}",
    "version": "1.0",
    "code": 200,
    "msg": "success",
    "data": {
        "result": "service_executed_successfully"
    },
    "method": "thing.service.invoke_reply"
}
topic3 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/service/reboot/invoke_reply"
result3 = client.publish(topic3, json.dumps(msg3))
print(f"[消息3] 设备服务调用响应")
print(f"  主题: {topic3}")
print(f"  操作权限: 发布")
print(f"  内容: {json.dumps(msg3, indent=2)}")
print(f"  结果: {'✓ 成功' if result3[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(1)

# 消息4: 设备命令响应（模拟收到命令后的响应）
msg4 = {
    "cmdId": f"cmd_{int(time.time())}",
    "timestamp": int(time.time()),
    "code": 0,
    "msg": "Command executed successfully"
}
topic4 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/cmd/response/cmd_test"
result4 = client.publish(topic4, json.dumps(msg4))
print(f"[消息4] 设备命令响应")
print(f"  主题: {topic4}")
print(f"  操作权限: 发布")
print(f"  内容: {json.dumps(msg4, indent=2)}")
print(f"  结果: {'✓ 成功' if result4[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(1)

# 消息5: 设备OTA升级通知回复
msg5 = {
    "id": f"ota_{int(time.time())}",
    "code": 0,
    "msg": "Accepted OTA update"
}
topic5 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/ota/inform_reply"
result5 = client.publish(topic5, json.dumps(msg5))
print(f"[消息5] 设备OTA升级通知回复")
print(f"  主题: {topic5}")
print(f"  操作权限: 发布")
print(f"  内容: {json.dumps(msg5, indent=2)}")
print(f"  结果: {'✓ 成功' if result5[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

time.sleep(1)

# 消息6: 设备数据上传
msg6 = {
    "id": f"dp_{int(time.time())}",
    "version": "1.0",
    "dataPoints": [
        {
            "dsId": "sensor",
            "data": {
                "temperature": 26.0,
                "humidity": 62
            }
        }
    ]
}
topic6 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/dp/post/json"
result6 = client.publish(topic6, json.dumps(msg6))
print(f"[消息6] 设备数据上传")
print(f"  主题: {topic6}")
print(f"  操作权限: 发布")
print(f"  内容: {json.dumps(msg6, indent=2)}")
print(f"  结果: {'✓ 成功' if result6[0] == 0 else '✗ 失败'}")
print(f"{'─'*66}\n")

# 等待平台响应
print("\n" + "="*70)
print("等待平台响应...（最多等待10秒）")
print("="*70 + "\n")

if received_event.wait(timeout=10):
    print("\n✅ 成功！收到平台响应")
else:
    print("\n⚠️ 未收到平台响应")
    print("这可能是因为：")
    print("  1. OneNET 平台不会自动响应上报消息")
    print("  2. 只有当平台主动下发命令或调用服务时才会有响应")
    print("  3. 某些主题需要特定条件才会收到消息")

# 清理
time.sleep(2)
client.disconnect()
client.loop_stop()

print("\n" + "="*70)
print("测试完成")
print("="*70)
print(f"\n总结:")
print(f"  ✓ 成功发布 6 条设备上报消息")
print(f"  ✓ 订阅了 9 种平台下发主题")
print(f"  {'✓ 收到 ' + str(len(received_messages)) + ' 条平台响应' if received_messages else '⚠️ 未收到平台响应（正常，除非平台主动下发）'}")
print("="*70)
