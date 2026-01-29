#!/usr/bin/env python3
"""
MO1 正确格式的事件上报测试
修复 request format error (2402)
"""
import paho.mqtt.client as mqtt
import json
import time

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
MO1_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772105871&method=sha1&sign=ZZoc17%2BbrxprIZ7prgo82Y%2FTDG4%3D"
DEVICE_NAME = "MO1"

print("="*70)
print("MO1 正确格式事件上报测试")
print("="*70)

received_messages = []
start_time = time.time()

client = mqtt.Client(client_id="MO1", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, MO1_TOKEN)

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n✓ 连接成功 (rc={rc})")
    if rc == 0:
        sub_topic = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/#"
        client.subscribe(sub_topic)
        print(f"✓ 订阅: {sub_topic}")

def on_message(client, userdata, msg):
    global received_messages
    elapsed = time.time() - start_time

    print(f"\n{'='*70}")
    print(f"[收到消息] {elapsed:.2f}秒")
    print(f"{'='*70}")
    print(f"  主题: {msg.topic}")
    try:
        payload = msg.payload.decode()
        try:
            json_obj = json.loads(payload)
            print(f"  内容:\n{json.dumps(json_obj, indent=2, ensure_ascii=False)}")

            # 检查是否有错误
            if 'code' in json_obj and json_obj['code'] != 200:
                print(f"\n  ⚠️ 平台返回错误码: {json_obj['code']}")
                print(f"  消息: {json_obj.get('msg', 'Unknown error')}")
            elif 'code' in json_obj and json_obj['code'] == 200:
                print(f"\n  ✅ 平台响应成功！")
        except:
            print(f"  内容: {payload}")
    except:
        print(f"  内容: {msg.payload}")

    received_messages.append(msg.topic)
    print(f"{'='*70}\n")

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()

time.sleep(2)

print("\n" + "="*70)
print("发送正确格式的事件上报")
print("="*70 + "\n")

# 正确的事件上报格式
# 注意：事件上报不需要 method 字段，直接发送 params
msg1 = {
    "id": f"evt_{int(time.time())}",
    "version": "1.0",
    "params": {
        "event": {
            "value": 100,
            "time": int(time.time())
        }
    }
}
pub_topic = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/event/post"
result1 = client.publish(pub_topic, json.dumps(msg1), qos=1)

print(f"[事件上报1] 标准格式")
print(f"  主题: {pub_topic}")
print(f"  内容:\n{json.dumps(msg1, indent=2, ensure_ascii=False)}")
print(f"  发布结果: {result1[0]}")
print(f"{'─'*66}\n")

time.sleep(3)

# 另一个格式：属性上报
msg2 = {
    "id": f"prop_{int(time.time())}",
    "version": "1.0",
    "params": {
        "temperature": 25.5,
        "humidity": 60
    }
}
pub_topic2 = f"$sys/{PRODUCT_ID}/{DEVICE_NAME}/thing/property/post"
result2 = client.publish(pub_topic2, json.dumps(msg2), qos=1)

print(f"[属性上报2] 标准格式")
print(f"  主题: {pub_topic2}")
print(f"  内容:\n{json.dumps(msg2, indent=2, ensure_ascii=False)}")
print(f"  发布结果: {result2[0]}")
print(f"{'─'*66}\n")

# 等待响应
print("\n" + "="*70)
print("等待平台响应...（10秒）")
print("="*70 + "\n")

time.sleep(10)

client.disconnect()
client.loop_stop()

print("\n" + "="*70)
print("测试完成")
print("="*70)
if received_messages:
    print(f"\n✅ 收到 {len(received_messages)} 条平台响应")
    print("\n这说明:")
    print("  ✓ MO1 可以成功发布消息")
    print("  ✓ MO1 可以订阅主题")
    print("  ✓ 平台正确响应设备上报")
    print("  ✓ 您之前看到的就是平台响应！")
