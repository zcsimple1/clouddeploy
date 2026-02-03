#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hmac
import hashlib
import time
from urllib.parse import quote

version = "2018-10-31"
method = "sha1"
device_name = "mo"
res = f"products/v6IkuqD6vh/devices/{device_name}"
et = int(time.time()) + (365 * 86400)

print("=" * 70)
print("设备级 Token (MO 设备) - 对比测试")
print("=" * 70)

# 密钥1: commonserv 配置中的密钥
print("\n【密钥1 - commonserv 配置】")
product_key_1 = "THNRWXNxUWxjSWNUOXNoN0pNalBGR3pKVHd3TDBkbjQ="
key1 = base64.b64decode(product_key_1)
string_for_signature = f"{et}\n{method}\n{res}\n{version}"
sign_bytes_1 = hmac.new(key1, string_for_signature.encode('utf-8'), hashlib.sha1).digest()
sign_1 = base64.b64encode(sign_bytes_1).decode('utf-8')
token_1 = f"version={version}&res={quote(res)}&et={et}&method={method}&sign={quote(sign_1)}"
print(f"密钥: {product_key_1}")
print(f"Username: v6IkuqD6vh")
print(f"Password: {token_1}")

# 密钥2: 用户之前提供的密钥
print("\n【密钥2 - 用户提供的】")
product_key_2 = "NHVWN09maHh3TTF6NFJ4TnRaeTBPeHpKaU8zQU9qaGQ="
key2 = base64.b64decode(product_key_2)
sign_bytes_2 = hmac.new(key2, string_for_signature.encode('utf-8'), hashlib.sha1).digest()
sign_2 = base64.b64encode(sign_bytes_2).decode('utf-8')
token_2 = f"version={version}&res={quote(res)}&et={et}&method={method}&sign={quote(sign_2)}"
print(f"密钥: {product_key_2}")
print(f"Username: v6IkuqD6vh")
print(f"Password: {token_2}")

print("\n" + "=" * 70)
print("在 MQTTX 中分别测试这两个 token")
print("=" * 70)
