# MQTT 设备接入

本目录包含 OneNET MQTT 设备接入相关的脚本和配置。

## 目录结构

```
mqtt/
├── 部署脚本
│   ├── setup-env.sh          # 环境依赖安装脚本
│   ├── setup-mqtt.sh         # MQTT 桥接服务安装脚本
│   ├── restart-mqtt.sh       # 快速重启 MQTT 桥接服务
│   └── mqtt-config.sh        # MQTT 配置信息
├── 工具
│   └── generate_onenet_token.py  # OneNET Token 生成工具
├── 测试脚本
│   ├── verify-mo.py          # 验证 MO 设备连接（本地快速测试）
│   ├── test-cloud.py         # 云服务器环境完整测试
│   ├── test-pubsub-final.py  # 完整的发布/订阅测试
│   └── test-simple.py        # 简单的连接、订阅、发布测试
└── 文档
    ├── README.md             # 本文件
    └── README.MQTT.md        # MQTT 详细配置说明
```

## 文件说明

### 核心部署脚本

- `setup-env.sh` - 环境依赖安装脚本（Python3、mosquitto-clients、paho-mqtt）
- `setup-mqtt.sh` - MQTT 桥接服务安装脚本,创建 systemd 服务
- `restart-mqtt.sh` - 快速重启 MQTT 桥接服务
- `mqtt-config.sh` - MQTT 配置信息

### Token 生成

- `generate_onenet_token.py` - OneNET Token 生成工具

### 测试脚本

- `verify-mo.py` - 验证使用设备 MO 连接和订阅（本地快速测试）
- `test-cloud.py` - 云服务器环境完整测试脚本
- `test-pubsub-final.py` - 完整的发布/订阅测试
- `test-simple.py` - 简单的连接、订阅、发布测试

### 文档

- `README.md` - 本文件，快速入门指南
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
# 快速验证 MO 设备连接
python3 verify-mo.py

# 完整测试（连接、订阅、发布）
python3 test-simple.py

# 完整的发布/订阅测试
python3 test-pubsub-final.py
```

### 2.1 环境准备（首次运行）

```bash
# 如果云服务器缺少依赖，先运行环境准备脚本
sudo bash setup-env.sh
```

此脚本会安装：
- Python3 和 pip3
- mosquitto-clients (MQTT 命令行工具)
- paho-mqtt (Python MQTT 库)

### 2.2 云服务器测试

```bash
# 在云服务器上运行完整环境测试
python3 test-cloud.py
```

**测试脚本说明**:
- `verify-mo.py` - 最简单的测试，只验证 MO 设备连接（15秒）
- `test-simple.py` - 包含连接、订阅、发布三个测试（约11秒）
- `test-pubsub-final.py` - 完整的发布/订阅测试（约8秒）
- `test-cloud.py` - 云服务器环境综合测试（包含4个测试，约15秒）

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
