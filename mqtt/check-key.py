#!/usr/bin/env python3
import base64

# 原始密钥
key1 = "THNRWXNxUWxjSWNUOXNoN0pNalBGR3pKVHd3TDBkbjQ="
decoded1 = base64.b64decode(key1).decode()
print(f"编码密钥: {key1}")
print(f"解码密钥: {decoded1}")
print(f"长度: {len(decoded1)}")

key2 = "wRdM7Q2i7m7FwG6B7n"
print(f"\n另一个密钥: {key2}")
print(f"长度: {len(key2)}")

# 尝试对 key2 进行编码
encoded2 = base64.b64encode(key2.encode()).decode()
print(f"编码后: {encoded2}")
