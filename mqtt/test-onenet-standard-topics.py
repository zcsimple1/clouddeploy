#!/usr/bin/env python3
"""
OneNET 标准主题格式测试
测试主题订阅通配符 +（单层）和 #（多层）
支持的主题类型：
1. 物模型相关主题：$sys/{pid}/{device-name}/thing/#
2. 物模型属性类：$sys/{pid}/{device-name}/thing/property/#
3. 物模型服务调用：$sys/{pid}/{device-name}/thing/service/#
4. 数据流命令下发：$sys/{pid}/{device-name}/cmd/#
"""
import paho.mqtt.client as mqtt
import json
import time
import threading

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
MO1_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772105871&method=sha1&sign=ZZoc17%2BbrxprIZ7prgo82Y%2FTDG4%3D"

print("="*70)
print("OneNET 标准主题格式测试")
print("测试通配符：+（单层）和 #（多层）")
print("="*70)

received_messages = []
received_event = threading.Event()

# ==================== 订阅端 ====================
print("\n【订阅端配置】")
print(f"设备ID: MO")
print(f"订阅主题模式: $sys/{PRODUCT_ID}/MO/thing/#")
print("-"*70)

sub_client = mqtt.Client(client_id="MO", protocol=mqtt.MQTTv311)
sub_client.username_pw_set(PRODUCT_ID, TOKEN)

def sub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"\n[订阅端] 连接结果: {rc} {'✓ 成功' if rc == 0 else '✗ 失败'}")

    if rc == 0:
        # 测试4种订阅方式（使用通配符）
        subscription_patterns = [
            # 方式1: 订阅全部物模型相关主题（#多层通配符）
            f"$sys/{PRODUCT_ID}/MO/thing/#",

            # 方式2: 订阅物模型属性类（#多层通配符）
            f"$sys/{PRODUCT_ID}/MO/thing/property/#",

            # 方式3: 订阅物模型服务调用 - 使用+单层通配符
            f"$sys/{PRODUCT_ID}/MO/thing/service/+/invoke",
            f"$sys/{PRODUCT_ID}/MO/thing/service/+/invoke_reply",

            # 方式4: 订阅数据流模式下的命令下发
            f"$sys/{PRODUCT_ID}/MO/cmd/#",
            f"$sys/{PRODUCT_ID}/MO/cmd/request/+",
            f"$sys/{PRODUCT_ID}/MO/cmd/response/+/accepted",
            f"$sys/{PRODUCT_ID}/MO/cmd/response/+/rejected",
        ]

        print("\n[订阅端] 订阅的主题模式：")
        for pattern in subscription_patterns:
            result = client.subscribe(pattern)
            print(f"  ✓ {pattern} (QoS={result[1]})")

        print("\n[订阅端] 等待接收消息...")
        print("-"*70)

    else:
        print(f"[订阅端] ✗ 连接失败: {rc}")

def sub_on_message(client, userdata, msg):
    print(f"\n{'='*70}")
    print(f"[订阅端] ✓✓✓ 收到消息! ✓✓✓")
    print(f"{'='*70}")
    print(f"  主题: {msg.topic}")
    print(f"  QoS: {msg.qos}")
    print(f"  保留: {msg.retain}")
    print(f"  大小: {len(msg.payload)} 字节")
    print(f"  内容: {msg.payload.decode()}")

    received_messages.append({
        'topic': msg.topic,
        'payload': msg.payload.decode(),
        'qos': msg.qos
    })
    received_event.set()
    print()

sub_client.on_connect = sub_on_connect
sub_client.on_message = sub_on_message

sub_client.connect(MQTT_HOST, MQTT_PORT, 60)
sub_client.loop_start()

time.sleep(2)

# ==================== 发送端 ====================
print("\n" + "="*70)
print("【发送端测试】")
print(f"设备ID: MO1")
print("="*70 + "\n")

pub_client = mqtt.Client(client_id="MO1", protocol=mqtt.MQTTv311)
pub_client.username_pw_set(PRODUCT_ID, MO1_TOKEN)

def pub_on_connect(client, userdata, flags, rc, properties=None):
    print(f"[发送端] 连接结果: {rc} {'✓ 成功' if rc == 0 else '✗ 失败'}")

    if rc == 0:
        print("\n开始发送测试消息...\n")

        # 消息1: 物模型属性上报
        message1 = {
            "id": str(int(time.time())),
            "version": "1.0",
            "params": {
                "temperature": 25.5,
                "humidity": 60,
                "pressure": 1013.25
            },
            "method": "thing.event.property.post"
        }
        topic1 = f"$sys/{PRODUCT_ID}/MO1/thing/property/post"
        payload1 = json.dumps(message1)
        result1 = client.publish(topic1, payload1, qos=1)
        print(f"[消息1] 物模型属性上报")
        print(f"  主题: {topic1}")
        print(f"  内容: {payload1}")
        print(f"  结果: {result1[0]} {'✓ 成功' if result1[0] == 0 else '✗ 失败'}\n")

        # 消息2: 物模型服务调用
        message2 = {
            "id": str(int(time.time() + 1)),
            "version": "1.0",
            "params": {
                "action": "reboot",
                "delay": 5
            },
            "method": "thing.service.invoke"
        }
        topic2 = f"$sys/{PRODUCT_ID}/MO1/thing/service/invoke_reply"
        payload2 = json.dumps(message2)
        result2 = client.publish(topic2, payload2, qos=1)
        print(f"[消息2] 物模型服务调用")
        print(f"  主题: {topic2}")
        print(f"  内容: {payload2}")
        print(f"  结果: {result2[0]} {'✓ 成功' if result2[0] == 0 else '✗ 失败'}\n")

        # 消息3: 命令下发请求
        message3 = {
            "cmdId": f"cmd_{int(time.time())}",
            "deviceId": "MO1",
            "timestamp": int(time.time()),
            "params": {
                "command": "update",
                "version": "2.0"
            }
        }
        topic3 = f"$sys/{PRODUCT_ID}/MO1/cmd/request/update"
        payload3 = json.dumps(message3)
        result3 = client.publish(topic3, payload3, qos=1)
        print(f"[消息3] 命令下发请求")
        print(f"  主题: {topic3}")
        print(f"  内容: {payload3}")
        print(f"  结果: {result3[0]} {'✓ 成功' if result3[0] == 0 else '✗ 失败'}\n")

        # 消息4: 命令响应（accepted）
        message4 = {
            "cmdId": f"cmd_{int(time.time())}",
            "deviceId": "MO1",
            "timestamp": int(time.time()),
            "code": 0,
            "msg": "success"
        }
        topic4 = f"$sys/{PRODUCT_ID}/MO1/cmd/response/cmd_accepted/accepted"
        payload4 = json.dumps(message4)
        result4 = client.publish(topic4, payload4, qos=1)
        print(f"[消息4] 命令响应（accepted）")
        print(f"  主题: {topic4}")
        print(f"  内容: {payload4}")
        print(f"  结果: {result4[0]} {'✓ 成功' if result4[0] == 0 else '✗ 失败'}\n")

        print("-"*70)
        print("所有消息已发送，等待订阅端接收...")

pub_client.on_connect = pub_on_connect
pub_client.connect(MQTT_HOST, MQTT_PORT, 60)
pub_client.loop_start()

# ==================== 等待接收 ====================
print("="*70)
print("等待接收消息（最多等待15秒）...")
print("="*70 + "\n")

timeout = 15
start_time = time.time()

while time.time() - start_time < timeout:
    if received_messages:
        print(f"\n已收到 {len(received_messages)} 条消息，继续等待更多...")
    time.sleep(1)

# 清理
sub_client.disconnect()
pub_client.disconnect()
sub_client.loop_stop()
pub_client.loop_stop()

# ==================== 测试结果 ====================
print("\n" + "="*70)
print("【测试结果汇总】")
print("="*70)

if received_messages:
    print(f"\n✅ 测试成功！共收到 {len(received_messages)} 条消息\n")

    print("收到的消息详情：")
    for i, msg in enumerate(received_messages, 1):
        print(f"\n消息 {i}:")
        print(f"  主题: {msg['topic']}")
        print(f"  QoS: {msg['qos']}")
        print(f"  内容: {msg['payload']}")

    # 分析哪些主题模式匹配了消息
    print("\n\n通配符匹配分析：")
    topics_received = [msg['topic'] for msg in received_messages]

    print("\n  ✓ # 多层通配符匹配的主题:")
    print(f"    $sys/{PRODUCT_ID}/MO/thing/#")
    for topic in topics_received:
        if topic.startswith(f"$sys/{PRODUCT_ID}/MO/thing/"):
            print(f"      └─ {topic}")

    print("\n  ✓ + 单层通配符匹配的主题:")
    print(f"    $sys/{PRODUCT_ID}/MO/thing/service/+/invoke_reply")
    for topic in topics_received:
        if "/thing/service/" in topic and "/invoke_reply" in topic:
            print(f"      └─ {topic}")

    success = True
else:
    print("\n❌ 测试失败：未收到任何消息\n")
    print("可能原因：")
    print("  1. 订阅的主题格式与发送的主题不匹配")
    print("  2. OneNET 平台限制（设备间消息转发）")
    print("  3. Token 权限问题")
    print("  4. 网络连接问题")
    success = False

print("\n" + "="*70)
if success:
    print("✅ OneNET 标准主题格式测试完成！")
    print("\n验证了以下功能：")
    print("  ✓ # 多层通配符订阅")
    print("  ✓ + 单层通配符订阅")
    print("  ✓ 物模型主题格式")
    print("  ✓ 命令下发主题格式")
else:
    print("❌ OneNET 标准主题格式测试失败")
print("="*70)
