# MQTT 设备接入

本目录包含 OneNET MQTT 设备接入相关的脚本和配置。

## 文件说明

### 核心脚本

- `setup-mqtt.sh` - MQTT 桥接服务安装脚本,创建 systemd 服务
- `restart-mqtt.sh` - 快速重启 MQTT 桥接服务
- `generate_onenet_token.py` - OneNET Token 生成工具

### 测试脚本

- `verify-mo.py` - 验证使用设备 MO 连接和订阅
- `test-*.py` / `test-*.sh` - 各种 MQTT 功能测试脚本

### 文档

- `README.MQTT.md` - MQTT 详细的配置和使用说明

## 快速开始

### 1. 生成 Token

```bash
# 产品级 Token (推荐,可订阅所有设备消息)
python3 generate_onenet_token.py --type product --product_id <产品ID> --product_key <产品Key> --duration 720

# 设备级 Token (用于特定设备)
python3 generate_onenet_token.py --type device --product_id <产品ID> --product_key <产品Key> --device_id <设备ID> --device_key <设备Key> --duration 720
```

### 2. 本地测试

```bash
# 验证连接
python3 verify-mo.py
```

### 3. 服务器部署

```bash
# 安装服务
bash setup-mqtt.sh

# 查看状态
sudo systemctl status elk-mqtt

# 查看日志
sudo journalctl -u elk-mqtt -f

# 重启服务
bash restart-mqtt.sh
```

## 配置说明

当前配置使用以下参数:

| 参数 | 值 |
|------|-----|
| Broker | `mqtts.heclouds.com:1883` |
| 用户名 | `v6IkuqD6vh` |
| 密码 | 见 `setup-mqtt.sh` |
| Client ID | `MO` |
| 订阅主题 | `$sys/v6IkuqD6vh/#` |

**注意**: 使用设备 MO 作为 Client ID,请确保 MO 未被其他客户端(如 MQTTX)占用。

## 工作流程

```
OneNET MQTT 设备
    ↓ MQTT 消息
mqtt-to-logstash.sh (mosquitto_sub)
    ↓ HTTP POST
Logstash (HTTP Input)
    ↓
Elasticsearch
    ↓
Kibana (可视化)
```

## 相关文档

- [ELK 部署指南](../README.ELK.md)
- [MQTT 详细说明](README.MQTT.md)
