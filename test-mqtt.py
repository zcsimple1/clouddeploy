#!/usr/bin/env python3
"""
OneNET MQTT 连接测试
测试订阅和发布消息
"""

import paho.mqtt.client as mqtt
import json
import time
import sys

# 配置
MQTT_HOST = "183.230.40.96"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"

# MO1 设备 Token
DEVICE_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772103681&method=sha1&sign=jVIWU3SNYRGjVL1c3nJTVuxNa1I%3D"
PRODUCT_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1772103681&method=sha1&sign=LMk4Z%2FJ0oaeY8BoEUr63M5INBeI%3D"

# 测试 1: 使用产品级 token 订阅
def test_product_subscribe():
    print("\n" + "="*50)
    print("测试 1: 使用产品级 Token 订阅")
    print("="*50)

    client = mqtt.Client(client_id=f"test-product-sub-{int(time.time())}", protocol=mqtt.MQTTv311)
    client.username_pw_set(PRODUCT_ID, PRODUCT_TOKEN)

    received_messages = []

    def on_connect(client, userdata, flags, rc):
        print(f"连接结果: {rc}")
        if rc == 0:
            print("✓ 连接成功!")
            client.subscribe(f"$sys/{PRODUCT_ID}/#")
            print(f"已订阅主题: $sys/{PRODUCT_ID}/#")
        else:
            print(f"✗ 连接失败,错误码: {rc}")

    def on_message(client, userdata, msg):
        print(f"收到消息:")
        print(f"  主题: {msg.topic}")
        print(f"  内容: {msg.payload.decode()}")
        received_messages.append(msg)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()

        # 等待连接和接收消息
        time.sleep(3)

        if client.is_connected():
            print("\n✓ 产品级 Token 订阅测试成功!")
            client.disconnect()
            return True
        else:
            print("\n✗ 产品级 Token 订阅测试失败!")
            return False
    except Exception as e:
        print(f"✗ 连接异常: {e}")
        return False
    finally:
        client.loop_stop()

# 测试 2: 使用设备级 token 订阅
def test_device_subscribe():
    print("\n" + "="*50)
    print("测试 2: 使用设备级 Token (MO1) 订阅")
    print("="*50)

    client = mqtt.Client(client_id=f"test-device-sub-{int(time.time())}", protocol=mqtt.MQTTv311)
    # 用户名格式: 产品ID&设备ID
    client.username_pw_set(f"{PRODUCT_ID}&MO1", DEVICE_TOKEN)

    def on_connect(client, userdata, flags, rc):
        print(f"连接结果: {rc}")
        if rc == 0:
            print("✓ 连接成功!")
            client.subscribe(f"$sys/{PRODUCT_ID}/#")
            print(f"已订阅主题: $sys/{PRODUCT_ID}/#")
        else:
            print(f"✗ 连接失败,错误码: {rc}")

    def on_message(client, userdata, msg):
        print(f"收到消息:")
        print(f"  主题: {msg.topic}")
        print(f"  内容: {msg.payload.decode()}")

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()

        time.sleep(3)

        if client.is_connected():
            print("\n✓ 设备级 Token 订阅测试成功!")
            client.disconnect()
            return True
        else:
            print("\n✗ 设备级 Token 订阅测试失败!")
            return False
    except Exception as e:
        print(f"✗ 连接异常: {e}")
        return False
    finally:
        client.loop_stop()

# 测试 3: 发布消息
def test_publish(device_id="MO"):
    print("\n" + "="*50)
    print(f"测试 3: 使用设备 {device_id} 发布消息")
    print("="*50)

    client = mqtt.Client(client_id=f"test-pub-{device_id}-{int(time.time())}", protocol=mqtt.MQTTv311)
    # 尝试使用产品级 token 发布
    client.username_pw_set(PRODUCT_ID, PRODUCT_TOKEN)

    def on_connect(client, userdata, flags, rc):
        print(f"连接结果: {rc}")
        if rc == 0:
            print("✓ 连接成功!")

            message = {
                "temperature": 25.5,
                "humidity": 60,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "device": device_id
            }
            topic = f"$sys/{PRODUCT_ID}/{device_id}/json"
            payload = json.dumps(message)

            print(f"发布到主题: {topic}")
            print(f"消息内容: {payload}")

            result = client.publish(topic, payload)
            print(f"发布结果: {result[0]} - {result[1]}")
            if result[0] == 0:
                print("✓ 消息发布成功!")
            else:
                print(f"✗ 消息发布失败: {result[1]}")
        else:
            print(f"✗ 连接失败,错误码: {rc}")

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()

        time.sleep(3)

        if client.is_connected():
            client.disconnect()
            return True
        return False
    except Exception as e:
        print(f"✗ 连接异常: {e}")
        return False
    finally:
        client.loop_stop()

if __name__ == "__main__":
    print("OneNET MQTT 连接测试")
    print("="*50)

    # 运行测试
    result1 = test_product_subscribe()
    result2 = test_device_subscribe()
    result3 = test_publish("MO")

    print("\n" + "="*50)
    print("测试总结:")
    print("="*50)
    print(f"产品级 Token 订阅: {'✓ 通过' if result1 else '✗ 失败'}")
    print(f"设备级 Token 订阅: {'✓ 通过' if result2 else '✗ 失败'}")
    print(f"消息发布测试:       {'✓ 通过' if result3 else '✗ 失败'}")
    print("="*50)
