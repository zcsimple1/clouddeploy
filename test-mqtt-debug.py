#!/usr/bin/env python3
"""
OneNET MQTT 连接详细调试测试
"""

import paho.mqtt.client as mqtt
import time
import sys

# 配置 (使用用户提供的成功配置)
MQTT_HOST = "mqtts.heclouds.com"
MQTT_PORT = 1883
PRODUCT_ID = "v6IkuqD6vh"
CLIENT_ID = "MO"

# 用户提供的成功 Token
PRODUCT_TOKEN = "version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"

def test_with_details():
    print("="*60)
    print("OneNET MQTT 连接调试测试")
    print("="*60)
    print(f"Broker: {MQTT_HOST}:{MQTT_PORT}")
    print(f"产品ID: {PRODUCT_ID}")
    print(f"Token: {PRODUCT_TOKEN}")
    print("="*60)

    client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
    client.username_pw_set(PRODUCT_ID, PRODUCT_TOKEN)

    def on_connect(client, userdata, flags, rc, properties=None):
        print(f"\n连接回调触发:")
        print(f"  返回码: {rc}")
        print(f"  Flags: {flags}")

        if rc == 0:
            print("\n✓ 连接成功!")
        else:
            error_codes = {
                0: "成功",
                1: "连接被拒绝 - 协议版本",
                2: "连接被拒绝 - 客户端ID",
                3: "连接被拒绝 - 服务器",
                4: "连接被拒绝 - 用户名或密码",
                5: "连接被拒绝 - 未授权"
            }
            print(f"\n✗ 连接失败!")
            print(f"  错误含义: {error_codes.get(rc, '未知')}")

    def on_disconnect(client, userdata, rc, properties=None):
        print(f"\n断开连接: {rc}")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # 启用调试日志
    client.enable_logger()

    print("\n尝试连接...")
    try:
        result = client.connect(MQTT_HOST, MQTT_PORT, 60)
        print(f"connect() 返回: {result}")

        client.loop_start()

        # 等待连接结果
        time.sleep(5)

        if client.is_connected():
            print("\n✓ 客户端状态: 已连接")
            client.disconnect()
            print("\n主动断开连接")
        else:
            print("\n✗ 客户端状态: 未连接")

    except Exception as e:
        print(f"\n✗ 连接异常: {type(e).__name__}: {e}")
    finally:
        client.loop_stop()

if __name__ == "__main__":
    test_with_details()
