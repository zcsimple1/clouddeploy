#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hmac
import hashlib
import time
from urllib.parse import quote

# 通过已知正确 token 反推密钥
# 已知 token: version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D
# URL 解码后的 sign: xhR6Azo+PoFz7Tw0iFA1uMKNXNs=
# 签名字符串: 1855626888\nsha1\nproducts/v6IkuqD6vh\n2018-10-31

# 基于已知参数推算密钥（这里需要正确的密钥才能生成新 token）
# 由于无法从签名反推密钥，使用用户提供的正确密钥

PRODUCT_KEY = "THNRWXNxUWxjSWNUOXNoN0pNalBGR3pKVHd3TDBkbjQ="  # commonserv 中的密钥
PRODUCT_ID = "v6IkuqD6vh"


def generate_onenet_token(res, expire_days=365, method="sha1"):
    """
    生成 OneNET Token

    Args:
        res: 资源路径（产品级或设备级）
        expire_days: 过期天数
        method: 签名方法
    """
    version = "2018-10-31"
    et = int(time.time()) + (expire_days * 86400)

    # 签名字符串（按 et, method, res, version 顺序）
    string_for_signature = f"{et}\n{method}\n{res}\n{version}"

    # 解码密钥
    key = base64.b64decode(PRODUCT_KEY)

    # 计算签名
    if method == "sha256":
        digest = hashlib.sha256
    elif method == "md5":
        digest = hashlib.md5
    else:  # sha1
        digest = hashlib.sha1

    sign_bytes = hmac.new(key, string_for_signature.encode('utf-8'), digest).digest()
    sign = base64.b64encode(sign_bytes).decode('utf-8')

    # URL 编码
    token = f"version={version}&res={quote(res)}&et={et}&method={method}&sign={quote(sign)}"

    return token, et


def generate_product_token(expire_days=365):
    """生成产品级 Token"""
    res = f"products/{PRODUCT_ID}"
    return generate_onenet_token(res, expire_days)


def generate_device_token(device_name, expire_days=365):
    """生成设备级 Token"""
    res = f"products/{PRODUCT_ID}/devices/{device_name}"
    return generate_onenet_token(res, expire_days)


if __name__ == "__main__":
    import sys

    # 支持命令行参数
    # python3 generate_onenet_token.py product [days]
    # python3 generate_onenet_token.py device mo [days]
    if len(sys.argv) >= 2:
        token_type = sys.argv[1]
        expire_days = int(sys.argv[2]) if len(sys.argv) > 2 else 365

        if token_type == "product":
            token, et = generate_product_token(expire_days)
            print(f"产品级 Token (过期 {expire_days} 天)")
            print(f"Username: {PRODUCT_ID}")
            print(f"Password: {token}")
            print(f"订阅主题: $sys/{PRODUCT_ID}/#")

        elif token_type == "device" and len(sys.argv) >= 3:
            device_name = sys.argv[2]
            token, et = generate_device_token(device_name, expire_days)
            print(f"设备级 Token ({device_name}, 过期 {expire_days} 天)")
            print(f"Username: {PRODUCT_ID}")
            print(f"Password: {token}")
            print(f"订阅主题: $sys/{PRODUCT_ID}/{device_name}/#")

        else:
            print("用法:")
            print("  python3 generate_onenet_token.py product [days]  # 生成产品级 token")
            print("  python3 generate_onenet_token.py device <device_name> [days]  # 生成设备级 token")
    else:
        # 默认生成产品级 token
        print("=" * 60)
        print("OneNET Token 生成工具")
        print("=" * 60)

        print("\n[产品级 Token]")
        token_prod, et_prod = generate_product_token(365)
        print(f"Username: {PRODUCT_ID}")
        print(f"Password: {token_prod}")
        print(f"订阅主题: $sys/{PRODUCT_ID}/#")

        print("\n[设备级 Token (MO)]")
        token_dev, et_dev = generate_device_token("mo", 365)
        print(f"Username: {PRODUCT_ID}")
        print(f"Password: {token_dev}")
        print(f"订阅主题: $sys/{PRODUCT_ID}/mo/#")

        print("\n使用方法:")
        print("  python3 generate_onenet_token.py product [days]  # 生成产品级 token")
        print("  python3 generate_onenet_token.py device <device_name> [days]  # 生成设备级 token")
        print("=" * 60)
