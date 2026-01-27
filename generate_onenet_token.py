#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import hmac
import time
from urllib.parse import quote


def generate_onenet_token(product_id, device_id, access_key, expire_hours=24):
    """
    生成 OneNET MQTT 设备级 Token

    参数:
        product_id: 产品 ID
        device_id: 设备 ID
        access_key: 设备密钥或 API Key
        expire_hours: Token 有效期（小时）

    返回:
        token 字符串
    """
    version = '2018-10-31'
    # 设备级资源路径
    res = f'products/{product_id}/devices/{device_id}'
    # 设置过期时间
    et = str(int(time.time()) + expire_hours * 3600)
    # 签名方法
    method = 'sha1'
    # 对 access_key 进行 decode
    key = base64.b64decode(access_key)
    # 计算 sign
    org = f'{et}\n{method}\n{res}\n{version}'
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()
    # value 部分进行 url 编码
    sign = quote(sign, safe='')
    res = quote(res, safe='')
    # token 参数拼接
    token = f'version={version}&res={res}&et={et}&method={method}&sign={sign}'

    return token


def generate_product_token(product_id, access_key, expire_hours=24):
    """
    生成 OneNET MQTT 产品级 Token

    参数:
        product_id: 产品 ID
        access_key: API Key
        expire_hours: Token 有效期（小时）

    返回:
        token 字符串
    """
    version = '2018-10-31'
    # 产品级资源路径
    res = f'products/{product_id}'
    # 设置过期时间
    et = str(int(time.time()) + expire_hours * 3600)
    # 签名方法
    method = 'sha1'
    # 对 access_key 进行 decode
    key = base64.b64decode(access_key)
    # 计算 sign
    org = f'{et}\n{method}\n{res}\n{version}'
    sign_b = hmac.new(key=key, msg=org.encode(), digestmod=method)
    sign = base64.b64encode(sign_b.digest()).decode()
    # value 部分进行 url 编码
    sign = quote(sign, safe='')
    res = quote(res, safe='')
    # token 参数拼接
    token = f'version={version}&res={res}&et={et}&method={method}&sign={sign}'

    return token


if __name__ == '__main__':
    # 配置信息
    PRODUCT_ID = 'v6IkuqD6vh'
    DEVICE_ID = 'MO'
    ACCESS_KEY = 'NHVWN09maHh3TTF6NFJ4TnRaeTBPeHpKaU8zQU9qaGQ='

    # 生成设备级 Token（推荐用于设备连接）
    print("=" * 60)
    print("设备级 Token（用于设备连接）:")
    print("=" * 60)
    device_token = generate_onenet_token(PRODUCT_ID, DEVICE_ID, ACCESS_KEY, expire_hours=720)  # 30天
    print(device_token)
    print()

    # 生成产品级 Token（用于产品级操作）
    print("=" * 60)
    print("产品级 Token（用于产品级操作）:")
    print("=" * 60)
    product_token = generate_product_token(PRODUCT_ID, ACCESS_KEY, expire_hours=720)
    print(product_token)
    print()
