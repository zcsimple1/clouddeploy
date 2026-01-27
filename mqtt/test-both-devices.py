#!/usr/bin/env python3
"""
完整测试 MO 和 MO1 的订阅和发布功能
每个测试只测试一个设备的能力
"""
import paho.mqtt.client as mqtt
import json
import time

MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"

# 配置
MO_PASS = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
MO1_PASS = "version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO&et=1772098636&method=sha1&sign=vzb4PV%2FK%2FvPLSdBd%2FVOVRHrSX44%3D"

def test_device_connect(device_id, password):
    """测试单个设备的连接能力"""
    print(f"\n测试: {device_id} 连接")

    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(PRODUCT_ID, password)

    connected = False

    def on_connect(client, userdata, flags, rc, properties=None):
        nonlocal connected
        if rc == 0:
            print(f"  ✓ 连接成功")
            connected = True
        else:
            print(f"  ✗ 连接失败 (错误码 {rc})")

    client.on_connect = on_connect

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    time.sleep(2)

    success = connected
    client.disconnect()
    client.loop_stop()

    time.sleep(1)

    return success

def test_device_publish(device_id, password):
    """测试单个设备的连接和发布能力"""
    print(f"\n测试: {device_id} 连接和发布")

    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(PRODUCT_ID, password)

    published = False

    def on_connect(client, userdata, flags, rc, properties=None):
        nonlocal published
        if rc == 0:
            print(f"  ✓ 连接成功")

            # 发布测试消息
            message = {"device": device_id, "test": "publish", "time": time.time()}
            topic = f"$sys/{PRODUCT_ID}/{device_id}/json"
            payload = json.dumps(message)

            print(f"  发布到: {topic}")
            result = client.publish(topic, payload)

            if result[0] == 0:
                print(f"  ✓ 发布成功")
                published = True
            else:
                print(f"  ✗ 发布失败")
        else:
            print(f"  ✗ 连接失败 (错误码 {rc})")

    client.on_connect = on_connect

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    time.sleep(3)

    success = published
    client.disconnect()
    client.loop_stop()

    time.sleep(1)

    return success

def test_device_subscribe(device_id, password):
    """测试单个设备的连接和订阅能力"""
    print(f"\n测试: {device_id} 连接和订阅")

    client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
    client.username_pw_set(PRODUCT_ID, password)

    subscribed = False

    def on_connect(client, userdata, flags, rc, properties=None):
        nonlocal subscribed
        if rc == 0:
            print(f"  ✓ 连接成功")

            # 订阅测试
            topic = f"$sys/{PRODUCT_ID}/#"
            client.subscribe(topic)
            print(f"  ✓ 订阅 {topic}")
            subscribed = True
        else:
            print(f"  ✗ 连接失败 (错误码 {rc})")

    client.on_connect = on_connect

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()

    time.sleep(2)

    success = subscribed
    client.disconnect()
    client.loop_stop()

    time.sleep(1)

    return success

if __name__ == "__main__":
    print("="*60)
    print("MQTT 设备功能测试")
    print("="*60)
    print(f"Broker: {MQTT_HOST}:{MQTT_PORT}")
    print(f"产品ID: {PRODUCT_ID}")
    print("="*60)

    # 测试 MO
    print("\n>>> 测试 MO")
    mo_conn = test_device_connect("MO", MO_PASS)
    mo_pub = test_device_publish("MO", MO_PASS)
    mo_sub = test_device_subscribe("MO", MO_PASS)

    # 测试 MO1
    print("\n>>> 测试 MO1")
    mo1_conn = test_device_connect("MO1", MO1_PASS)
    mo1_pub = test_device_publish("MO1", MO1_PASS)
    mo1_sub = test_device_subscribe("MO1", MO1_PASS)

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"MO:")
    print(f"  连接:  {'✓' if mo_conn else '✗'}")
    print(f"  发布:  {'✓' if mo_pub else '✗'}")
    print(f"  订阅:  {'✓' if mo_sub else '✗'}")
    print(f"MO1:")
    print(f"  连接:  {'✓' if mo1_conn else '✗'}")
    print(f"  发布:  {'✓' if mo1_pub else '✗'}")
    print(f"  订阅:  {'✓' if mo1_sub else '✗'}")
    print("="*60)

    all_pass = mo_conn and mo_pub and mo_sub and mo1_conn and mo1_pub and mo1_sub
    if all_pass:
        print("\n✓ 所有测试通过!")
        print("\n建议配置:")
        print("  - 使用 MO 或 MO1 任意一个设备作为桥接服务的 Client ID")
        print("  - 该设备可订阅所有设备消息")
        print("  - 确保该设备未被其他客户端(如MQTTX)占用")
        exit(0)
    else:
        print("\n✗ 部分测试失败")
        if not mo1_conn:
            print("  - MO1 连接失败 (可能被MQTTX或其他客户端占用)")
        if not mo_conn:
            print("  - MO 连接失败 (可能被占用)")
        exit(1)
