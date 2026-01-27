#!/usr/bin/env python3
"""
测试两组 MQTT 配置的发布和订阅
"""

import paho.mqtt.client as mqtt
import json
import time
import threading

# 配置组 1: 产品级 Token (主用)
CONFIG_1 = {
    "host": "mqtts.heclouds.com",
    "port": 1883,
    "user": "v6IkuqD6vh",
    "token": "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D",
    "name": "产品级Token (主用)"
}

# 配置组 2: 设备级 Token (备用)
CONFIG_2 = {
    "host": "mqtts.heclouds.com",
    "port": 1883,
    "user": "v6IkuqD6vh",
    "token": "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO&et=1772098636&method=sha1&sign=vzb4PV%2FK%2FvPLSdBd%2FVOVRHrSX44%3D",
    "name": "设备级Token MO (备用)"
}

PRODUCT_ID = "v6IkuqD6vh"

def test_connection(config, client_id):
    """测试连接"""
    print("\n" + "="*60)
    print(f"测试配置: {config['name']}")
    print("="*60)
    print(f"Broker: {config['host']}:{config['port']}")
    print(f"用户名: {config['user']}")
    print(f"Client ID: {client_id}")
    print(f"Token: {config['token'][:50]}...")
    print("="*60)

    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(config['user'], config['token'])

    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"连接结果: {rc}")
        if rc == 0:
            print("✓ 连接成功!")
        else:
            print(f"✗ 连接失败,错误码: {rc}")

    client.on_connect = on_connect

    try:
        client.connect(config['host'], config['port'], 60)
        client.loop_start()
        time.sleep(3)

        result = client.is_connected()
        client.disconnect()
        client.loop_stop()

        return result
    except Exception as e:
        print(f"✗ 异常: {e}")
        client.loop_stop()
        return False

def test_pubsub(config, pub_device, sub_client_id):
    """测试发布和订阅"""
    print("\n" + "="*60)
    print(f"测试发布和订阅: {config['name']}")
    print(f"发布设备: {pub_device}")
    print(f"订阅Client ID: {sub_client_id}")
    print("="*60)

    received = threading.Event()
    received_data = {}

    # 订阅端
    sub_client = mqtt.Client(client_id=sub_client_id, protocol=mqtt.MQTTv311)
    sub_client.username_pw_set(config['user'], config['token'])

    def sub_on_connect(client, userdata, flags, rc, properties=None):
        print(f"订阅端连接: {rc}")
        if rc == 0:
            topic = f"$sys/{PRODUCT_ID}/#"
            client.subscribe(topic)
            print(f"订阅主题: {topic}")
        else:
            print(f"✗ 订阅端连接失败: {rc}")

    def sub_on_message(client, userdata, msg):
        print(f"\n✓ 收到消息!")
        print(f"  主题: {msg.topic}")
        print(f"  内容: {msg.payload.decode()}")
        received_data['topic'] = msg.topic
        received_data['payload'] = msg.payload.decode()
        received.set()

    sub_client.on_connect = sub_on_connect
    sub_client.on_message = sub_on_message

    # 发布端
    pub_client = mqtt.Client(client_id=pub_device, protocol=mqtt.MQTTv311)
    pub_client.username_pw_set(config['user'], config['token'])

    def pub_on_connect(client, userdata, flags, rc, properties=None):
        print(f"发布端连接: {rc}")
        if rc == 0:
            time.sleep(1)

            message = {
                "temperature": 28.5,
                "humidity": 65,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "device": pub_device,
                "test": config['name']
            }
            topic = f"$sys/{PRODUCT_ID}/{pub_device}/json"
            payload = json.dumps(message)

            print(f"\n发送消息:")
            print(f"  主题: {topic}")
            print(f"  内容: {payload}")

            result = client.publish(topic, payload)
            print(f"发布结果: {result[0]} - {result[1]}")
            if result[0] == 0:
                print("✓ 消息发布成功!")

    pub_client.on_connect = pub_on_connect

    try:
        # 启动订阅端
        sub_client.connect(config['host'], config['port'], 60)
        sub_client.loop_start()
        time.sleep(2)

        # 启动发布端
        pub_client.connect(config['host'], config['port'], 60)
        pub_client.loop_start()

        # 等待接收消息
        if received.wait(timeout=10):
            print("\n✓ 发布订阅测试成功!")
            success = True
        else:
            print("\n✗ 未收到消息")
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
    print("="*60)
    print("OneNET MQTT 配置测试")
    print("="*60)

    print("\n>>> 测试配置1连接 (随机Client ID)")
    result1 = test_connection(CONFIG_1, f"bridge-{int(time.time())}")

    print("\n>>> 测试配置2连接 (设备MO作为Client ID)")
    result2 = test_connection(CONFIG_2, "MO")

    print("\n>>> 测试配置1发布订阅")
    result3 = test_pubsub(CONFIG_1, "MO1", f"sub-{int(time.time())}")

    print("\n>>> 测试配置2发布订阅 (需要断开MQTTX的MO连接)")
    print("注意: 如果MO已被MQTTX占用,测试2会失败")
    result4 = test_pubsub(CONFIG_2, "MO1", "MO")

    print("\n" + "="*60)
    print("测试总结:")
    print("="*60)
    print(f"配置1连接:    {'✓ 通过' if result1 else '✗ 失败'} - {CONFIG_1['name']}")
    print(f"配置2连接:    {'✓ 通过' if result2 else '✗ 失败'} - {CONFIG_2['name']}")
    print(f"配置1发布订阅: {'✓ 通过' if result3 else '✗ 失败'}")
    print(f"配置2发布订阅: {'✓ 通过' if result4 else '✗ 失败'}")
    print("="*60)

    print("\n推荐配置:")
    if result1 and result3:
        print("✓ 使用配置1 (产品级 Token + 随机 Client ID)")
        print(f"  Broker: {CONFIG_1['host']}")
        print(f"  用户名: {CONFIG_1['user']}")
        print(f"  Token: {CONFIG_1['token']}")
        print("  Client ID: 随机生成 (如 bridge-timestamp)")
    elif result2 and result4:
        print("✓ 使用配置2 (设备级 Token + 设备MO作为Client ID)")
        print(f"  Broker: {CONFIG_2['host']}")
        print(f"  用户名: {CONFIG_2['user']}")
        print(f"  Token: {CONFIG_2['token']}")
        print("  Client ID: MO")
        print("  注意: 需确保MO未被其他客户端占用")
