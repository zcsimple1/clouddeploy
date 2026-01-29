#!/usr/bin/env python3
"""
向 MO 设备发送测试消息
用于配合 test-mo-subscribe.py 使用
"""
import paho.mqtt.client as mqtt
import json
import time

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
MO_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
MO1_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772105871&method=sha1&sign=ZZoc17%2BbrxprIZ7prgo82Y%2FTDG4%3D"

print("="*70)
print("向 MO 设备发送测试消息")
print("="*70)

# 使用 MO1 作为发送端
client = mqtt.Client(client_id="MO1", protocol=mqtt.MQTTv311)
client.username_pw_set(PRODUCT_ID, MO1_TOKEN)

sent_count = 0

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n✓ 连接成功 (rc={rc})")

    if rc == 0:
        print("\n开始发送测试消息...\n")

        # 消息1: 物模型属性上报
        msg1 = {
            "id": "msg_1",
            "version": "1.0",
            "params": {
                "temperature": 25.5,
                "humidity": 60,
                "pressure": 1013.25
            },
            "method": "thing.event.property.post"
        }
        topic1 = f"$sys/{PRODUCT_ID}/MO1/thing/property/post"
        send_message(client, topic1, msg1, 1, "物模型属性上报")

        time.sleep(1)

        # 消息2: 物模型事件上报
        msg2 = {
            "id": "msg_2",
            "version": "1.0",
            "params": {
                "event": "temperature_alert",
                "value": 35.5,
                "threshold": 30.0
            },
            "method": "thing.event.post"
        }
        topic2 = f"$sys/{PRODUCT_ID}/MO1/thing/event/post"
        send_message(client, topic2, msg2, 1, "物模型事件上报")

        time.sleep(1)

        # 消息3: 物模型服务调用回复
        msg3 = {
            "id": "msg_3",
            "code": 200,
            "msg": "success",
            "data": {
                "result": "service_executed"
            },
            "method": "thing.service.property.set_reply"
        }
        topic3 = f"$sys/{PRODUCT_ID}/MO1/thing/service/property/set_reply"
        send_message(client, topic3, msg3, 1, "物模型服务调用回复")

        time.sleep(1)

        # 消息4: 命令下发请求
        msg4 = {
            "cmdId": f"cmd_{int(time.time())}",
            "timestamp": int(time.time()),
            "params": {
                "command": "update_firmware",
                "version": "2.0.1",
                "url": "https://example.com/firmware.bin"
            }
        }
        topic4 = f"$sys/{PRODUCT_ID}/MO/cmd/request/update"
        send_message(client, topic4, msg4, 1, "命令下发请求")

        time.sleep(1)

        # 消息5: 命令响应 accepted
        msg5 = {
            "cmdId": f"cmd_{int(time.time())}",
            "timestamp": int(time.time()),
            "code": 0,
            "msg": "Command accepted"
        }
        topic5 = f"$sys/{PRODUCT_ID}/MO/cmd/response/accepted/accepted"
        send_message(client, topic5, msg5, 1, "命令响应 accepted")

        time.sleep(1)

        # 消息6: 自定义数据主题
        msg6 = {
            "device": "MO1",
            "test": "custom_data",
            "data": {
                "value": 123,
                "unit": "celsius"
            },
            "timestamp": time.time()
        }
        topic6 = f"$sys/{PRODUCT_ID}/MO/custom/data"
        send_message(client, topic6, msg6, 0, "自定义数据主题")

        print("\n" + "="*70)
        print(f"✓ 所有消息已发送！共 {sent_count} 条")
        print("="*70)
        print("\n请检查订阅端（MO）是否收到这些消息")
        print("运行命令：python3 test-mo-subscribe.py")

def send_message(client, topic, payload_dict, qos, description):
    global sent_count
    payload = json.dumps(payload_dict, indent=2)
    result = client.publish(topic, payload, qos=qos)

    sent_count += 1
    status = "✓" if result[0] == 0 else "✗"

    print(f"[消息 {sent_count}] {description}")
    print(f"  主题: {topic}")
    print(f"  QoS: {qos}")
    print(f"  状态: {status}")
    print(f"  内容: {payload}")
    print(f"  {'─'*66}\n")

def on_publish(client, userdata, mid):
    pass

client.on_connect = on_connect
client.on_publish = on_publish

try:
    print(f"\n连接信息:")
    print(f"  Broker: {MQTT_HOST}:{MQTT_PORT}")
    print(f"  Client ID: MO1")
    print(f"  发送目标: MO 设备")
    print("="*70)

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("\n\n用户中断，退出...")
    print(f"\n发送统计: {sent_count} 条消息")

except Exception as e:
    print(f"\n错误: {e}")

finally:
    client.disconnect()
    print("\n发送端结束")
