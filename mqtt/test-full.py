#!/usr/bin/env python3
"""
OneNET MQTT 完整测试 - 订阅和发布
"""

import paho.mqtt.client as mqtt
import json
import time
import threading

# 配置 (使用用户提供的成功配置)
MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
PRODUCT_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

# 测试结果
test_results = {
    "subscribe": False,
    "publish": False,
    "receive_message": False
}

# 测试 1: 订阅测试
def test_subscribe(device_id="MO"):
    print("="*60)
    print(f"测试 1: 订阅设备 {device_id} 的消息")
    print("="*60)

    # 使用已注册的设备作为 Client ID
    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(PRODUCT_ID, PRODUCT_TOKEN)

    received_messages = []

    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"连接结果: {rc}")
        if rc == 0:
            print("✓ 连接成功!")
            # 订阅设备数据
            topic = f"$sys/{PRODUCT_ID}/{device_id}/json"
            client.subscribe(topic)
            print(f"已订阅主题: {topic}")
            test_results["subscribe"] = True
        else:
            print(f"✗ 连接失败,错误码: {rc}")

    def on_message(client, userdata, msg):
        print(f"\n收到消息!")
        print(f"  主题: {msg.topic}")
        print(f"  内容: {msg.payload.decode()}")
        received_messages.append(msg)
        test_results["receive_message"] = True

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()

        # 保持订阅状态 30 秒
        print("\n等待接收消息... (30秒)")
        time.sleep(30)

        client.disconnect()
        print(f"\n共收到 {len(received_messages)} 条消息")

        return test_results["receive_message"]
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False
    finally:
        client.loop_stop()

# 测试 2: 发布测试
def test_publish(device_id="MO1"):
    print("\n" + "="*60)
    print(f"测试 2: 使用设备 {device_id} 发布消息")
    print("="*60)

    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(PRODUCT_ID, PRODUCT_TOKEN)

    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"连接结果: {rc}")
        if rc == 0:
            print("✓ 连接成功!")

            message = {
                "temperature": 25.5,
                "humidity": 60,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "device": device_id,
                "test": "python mqtt test"
            }
            topic = f"$sys/{PRODUCT_ID}/{device_id}/json"
            payload = json.dumps(message)

            print(f"\n发布到主题: {topic}")
            print(f"消息内容: {payload}")

            result = client.publish(topic, payload)
            print(f"发布结果: {result[0]} - {result[1]}")
            if result[0] == 0:
                print("✓ 消息发布成功!")
                test_results["publish"] = True
            else:
                print(f"✗ 消息发布失败: {result[1]}")
        else:
            print(f"✗ 连接失败,错误码: {rc}")

    try:
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()

        time.sleep(3)
        client.disconnect()
        return test_results["publish"]
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False
    finally:
        client.loop_stop()

# 测试 3: 发布和订阅双向测试
def test_bidirectional(pub_device="MO1", sub_device="MO"):
    print("\n" + "="*60)
    print(f"测试 3: 双向测试 - {sub_device}订阅, {pub_device}发布")
    print("="*60)

    received = threading.Event()
    received_message = {}

    # 订阅客户端
    sub_client = mqtt.Client(client_id=f"sub-{sub_device}-{int(time.time())}", protocol=mqtt.MQTTv311)
    sub_client.username_pw_set(PRODUCT_ID, PRODUCT_TOKEN)

    def sub_on_connect(client, userdata, flags, rc, properties=None):
        print(f"订阅端连接: {rc}")
        if rc == 0:
            # 订阅所有设备的消息
            topic = f"$sys/{PRODUCT_ID}/#"
            client.subscribe(topic)
            print(f"订阅端已订阅: {topic}")
        else:
            print(f"✗ 订阅端连接失败,错误码: {rc}")

    def sub_on_message(client, userdata, msg):
        print(f"\n订阅端收到消息:")
        print(f"  主题: {msg.topic}")
        print(f"  内容: {msg.payload.decode()}")
        received_message["topic"] = msg.topic
        received_message["payload"] = msg.payload.decode()
        received.set()

    sub_client.on_connect = sub_on_connect
    sub_client.on_message = sub_on_message

    # 发布客户端
    pub_client = mqtt.Client(client_id=pub_device, protocol=mqtt.MQTTv311)
    pub_client.username_pw_set(PRODUCT_ID, PRODUCT_TOKEN)

    def pub_on_connect(client, userdata, flags, rc, properties=None):
        print(f"发布端连接: {rc}")
        if rc == 0:
            time.sleep(1)  # 等待订阅端准备好

            message = {
                "temperature": 30.5,
                "humidity": 55,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "device": pub_device,
                "test": "bidirectional test"
            }
            topic = f"$sys/{PRODUCT_ID}/{pub_device}/json"
            payload = json.dumps(message)

            print(f"\n发布端发送:")
            print(f"  主题: {topic}")
            print(f"  内容: {payload}")

            client.publish(topic, payload)

    pub_client.on_connect = pub_on_connect

    try:
        # 启动订阅端
        sub_client.connect(MQTT_HOST, MQTT_PORT, 60)
        sub_client.loop_start()

        time.sleep(2)  # 等待订阅端就绪

        # 启动发布端
        pub_client.connect(MQTT_HOST, MQTT_PORT, 60)
        pub_client.loop_start()

        # 等待接收消息
        if received.wait(timeout=10):
            print("\n✓ 双向通信测试成功!")
            success = True
        else:
            print("\n✗ 未收到消息,双向通信测试失败!")
            success = False

        sub_client.disconnect()
        pub_client.disconnect()

        return success
    except Exception as e:
        print(f"✗ 异常: {e}")
        return False
    finally:
        sub_client.loop_stop()
        pub_client.loop_stop()

if __name__ == "__main__":
    print("OneNET MQTT 完整功能测试")
    print("="*60)
    print(f"Broker: {MQTT_HOST}:{MQTT_PORT}")
    print(f"产品ID: {PRODUCT_ID}")
    print("="*60)

    # 运行测试
    print("\n\n>>> 运行发布测试...")
    test_publish("MO1")

    print("\n\n>>> 运行双向测试...")
    result = test_bidirectional("MO1", "MO")

    print("\n\n>>> 订阅测试 (将监听30秒,请在另一终端用MQTTX发送消息)...")
    print("    提示: 你可以用MQTTX向以下主题发布消息:")
    print(f"    $sys/{PRODUCT_ID}/MO/json")
    print(f"    $sys/{PRODUCT_ID}/MO1/json")
    test_subscribe("MO")

    print("\n" + "="*60)
    print("测试总结:")
    print("="*60)
    print(f"发布测试:       {'✓ 通过' if test_results['publish'] else '✗ 失败'}")
    print(f"双向通信测试:   {'✓ 通过' if result else '✗ 失败'}")
    print(f"接收消息:       {'✓ 通过' if test_results['receive_message'] else '✗ 失败'}")
    print("="*60)
