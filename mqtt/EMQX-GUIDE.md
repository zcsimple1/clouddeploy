# EMQX 私有 MQTT 服务器部署指南

## 概述

EMQX 是一个开源的 MQTT Broker，提供私有 MQTT 服务器功能。本项目已将 EMQX 集成到 Docker Compose 环境中。

---

## 快速开始

### 1. 部署服务

```bash
cd /Users/zora/Documents/Work/mygithub/clouddeploy
sudo bash deploy-emqx.sh
```

### 2. 访问 EMQX Dashboard

打开浏览器访问：
```
http://localhost:18083
```

默认登录：
- 用户名: `admin`
- 密码: `public`

---

## 服务端口

### MQTT 端口

| 端口 | 协议 | 说明 |
|------|------|------|
| 1883 | MQTT/TCP | 标准 MQTT 连接 |
| 8883 | MQTT/TLS | 加密 MQTT 连接 (SSL) |
| 8083 | MQTT/WS | WebSocket MQTT |
| 8084 | MQTT/WSS | 安全 WebSocket MQTT (WSS) |

### 管理端口

| 端口 | 协议 | 说明 |
|------|------|------|
| 18083 | HTTP | EMQX Dashboard |
| 18084 | HTTPS | EMQX Dashboard (安全) |
| 5369 | gRPC | EMQX API |

---

## MQTT 客户端连接示例

### 使用 Python (paho-mqtt)

```python
import paho.mqtt.client as mqtt

# 连接配置
broker = "localhost"
port = 1883
client_id = "python_client_1"

# 回调函数
def on_connect(client, userdata, flags, rc):
    print(f"连接成功: {rc}")
    client.subscribe("test/#")

def on_message(client, userdata, msg):
    print(f"主题: {msg.topic}, 消息: {msg.payload.decode()}")

# 创建客户端
client = mqtt.Client(client_id=client_id)
client.on_connect = on_connect
client.on_message = on_message

# 连接
client.connect(broker, port, 60)
client.loop_forever()

# 发布消息
client.publish("test/topic", "Hello EMQX!")
```

### 使用 MQTTX 桌面客户端

1. 下载 MQTTX: https://mqttx.app/zh
2. 新建连接：
   - Host: `localhost`
   - Port: `1883`
   - Client ID: 任意（如 `mqttx_client`）
   - 用户名/密码: 可选（EMQX 默认允许匿名访问）
3. 点击"连接"

### 使用 Node.js (mqtt.js)

```javascript
const mqtt = require('mqtt');

const client = mqtt.connect('mqtt://localhost:1883');

client.on('connect', () => {
  console.log('已连接到 EMQX');

  // 订阅主题
  client.subscribe('test/#');

  // 发布消息
  client.publish('test/topic', 'Hello from Node.js');
});

client.on('message', (topic, message) => {
  console.log(`收到消息: ${topic} - ${message.toString()}`);
});
```

---

## EMQX Dashboard 使用

### 1. 概览页面

查看：
- 连接数
- 消息速率
- 订阅数
- 系统资源使用情况

### 2. 客户端管理

路径: `管理 -> 客户端`

查看所有连接的客户端信息：
- Client ID
- Username
- IP 地址
- 连接时间

### 3. 订阅管理

路径: `管理 -> 订阅`

查看所有订阅的主题和客户端。

### 4. 认证管理

#### 创建用户

路径: `访问控制 -> 认证`

点击"创建"：
- 用户名: `test_user`
- 密码: `test_password`

#### 设置 ACL 规则

路径: `访问控制 -> 授权`

创建规则限制客户端访问：
```
规则类型: 发布
主题: test/#
动作: 允许
```

### 5. 规则引擎（消息转发）

路径: `数据桥接 -> 规则`

创建规则将消息转发到 Logstash：

```sql
SELECT
  topic,
  payload,
  qos,
  clientid,
  username,
  timestamp
FROM
  "#"
```

添加动作：
- 类型: Webhook
- URL: `http://logstash:5000/emqx`
- 方法: POST
- 内容类型: application/json

---

## 集成到 ELK

### 方案 1: 使用规则引擎（推荐）

1. 在 EMQX Dashboard 创建规则
2. 添加动作: Webhook
3. URL: `http://logstash:5000/emqx`

### 方案 2: 使用 Logstash TCP 输入

Logstash 配置：

```ruby
input {
  tcp {
    port => 5001
    codec => json_lines
    tags => ["emqx"]
  }
}

filter {
  if "emqx" in [tags] {
    # 处理 MQTT 消息
    mutate {
      add_field => {
        "service" => "emqx"
        "type" => "mqtt_message"
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "emqx-mqtt-%{+YYYY.MM.dd}"
  }
}
```

### Kibana 查看数据

1. 打开 Kibana: `http://localhost:5601`
2. 进入 `Stack Management` -> `Index Patterns`
3. 创建索引模式: `emqx-mqtt-*`
4. 进入 `Discover` 查看数据

---

## 常用操作

### 启动服务

```bash
docker compose -f docker-compose.emqx.yml up -d
```

### 停止服务

```bash
docker compose -f docker-compose.emqx.yml down
```

### 查看日志

```bash
# 所有服务日志
docker compose -f docker-compose.emqx.yml logs -f

# 仅 EMQX 日志
docker compose -f docker-compose.emqx.yml logs -f emqx
```

### 重启服务

```bash
docker compose -f docker-compose.emqx.yml restart emqx
```

### 进入容器

```bash
docker exec -it emqx sh
```

### 备份数据

```bash
# 备份 EMQX 数据
tar -czf emqx-backup-$(date +%Y%m%d).tar.gz /root/data/emqx

# 备份 ELK 数据
tar -czf elk-backup-$(date +%Y%m%d).tar.gz /root/data/elk
```

---

## 安全建议

### 生产环境配置

1. **禁用匿名访问**

在 `docker-compose.emqx.yml` 中修改：
```yaml
environment:
  - EMQX__ALLOW_ANONYMOUS=false
```

2. **修改默认密码**

登录 Dashboard 后修改 admin 密码。

3. **启用 TLS/SSL**

```yaml
ports:
  - "8883:8883"  # MQTT over TLS
volumes:
  - ./emqx-certificates:/opt/emqx/etc/certs
```

4. **限制 IP 访问**

```yaml
environment:
  - EMQX__LISTENER__TCP__EXTERNAL__MAX_CONNECTIONS=1000
```

5. **设置访问控制列表 (ACL)**

限制客户端只能访问特定主题：
```
用户: device_001
允许: device/001/#
拒绝: #
```

---

## 故障排查

### 问题 1: 无法连接 EMQX

**检查：**
```bash
# EMQX 是否运行
docker ps | grep emqx

# 端口是否开放
telnet localhost 1883

# 查看日志
docker logs emqx
```

### 问题 2: 日志未发送到 Logstash

**检查：**
```bash
# Logstash 是否运行
docker ps | grep logstash

# 网络连接
docker exec emqx ping logstash

# Logstash 日志
docker logs logstash
```

### 问题 3: Dashboard 无法访问

**检查：**
```bash
# 端口是否正确
netstat -tlnp | grep 18083

# 浏览器控制台错误
# 检查是否是 HTTPS 问题（尝试使用 http://）
```

### 问题 4: 消息未存储到 Elasticsearch

**检查：**
```bash
# Elasticsearch 状态
curl http://localhost:9200/_cluster/health

# 查看索引
curl http://localhost:9200/_cat/indices

# Logstash 配置
docker exec logstash cat /usr/share/logstash/pipeline/logstash.conf
```

---

## 监控和性能

### EMQX 性能优化

1. **调整连接数限制**

```yaml
environment:
  - EMQX__LISTENER__TCP__EXTERNAL__MAX_CONNECTIONS=10000
```

2. **启用集群模式**

如果需要高可用，部署多个 EMQX 节点并配置集群。

3. **消息持久化**

```yaml
environment:
  - EMQX__MQTT__MAX_TOPIC_LEVELS=10
```

### 监控指标

使用 EMQX Dashboard 查看：
- 连接数趋势
- 消息吞吐量
- 系统资源使用
- 延迟统计

---

## 参考资源

- EMQX 官方文档: https://www.emqx.io/docs/
- MQTT 协议规范: http://mqtt.org/
- ELK 官方文档: https://www.elastic.co/guide/
