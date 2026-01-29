# EMQX 私有 MQTT 服务器

## 简介

本项目已集成 **EMQX** - 一个高性能、可扩展的开源 MQTT 消息服务器，配合 ELK Stack 实现完整的 IoT 数据收集和分析解决方案。

---

## 架构图

```
┌─────────────┐
│  IoT 设备   │
└──────┬──────┘
       │ MQTT
       ▼
┌──────────────────┐
│   EMQX Broker   │  ← 私有 MQTT 服务器
│  (localhost:1883)│
└──────┬───────────┘
       │ HTTP Webhook
       ▼
┌──────────────┐
│  Logstash   │  ← 数据处理
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Elasticsearch   │  ← 数据存储
└──────┬───────────┘
       │
       ▼
┌──────────────┐
│   Kibana    │  ← 数据可视化
└──────────────┘
```

---

## 快速开始

### 1. 部署服务

```bash
cd /Users/zora/Documents/Work/mygithub/clouddeploy
sudo bash deploy-emqx.sh
```

### 2. 测试服务

```bash
bash mqtt/test-emqx.sh
```

### 3. 访问管理界面

- **EMQX Dashboard**: http://localhost:18083
  - 用户名: `admin`
  - 密码: `public`

- **Kibana**: http://localhost:5601

---

## 文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `docker-compose.emqx.yml` | EMQX + ELK Docker Compose 配置 |
| `deploy-emqx.sh` | 一键部署脚本 |
| `mqtt/test-emqx.sh` | EMQX 功能测试脚本 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `mqtt/emqx-bridges.conf` | EMQX 到 Logstash 的桥接配置 |
| `mqtt/logstash-emqx.conf` | Logstash 接收 EMQX 消息的配置 |
| `mqtt/EMQX-GUIDE.md` | EMQX 详细使用指南 |

---

## 服务端口

### MQTT 端口

| 端口 | 协议 | 说明 |
|------|------|------|
| 1883 | MQTT/TCP | 标准 MQTT 连接 |
| 8883 | MQTT/TLS | 加密 MQTT 连接 |
| 8083 | MQTT/WS | WebSocket MQTT |
| 8084 | MQTT/WSS | 安全 WebSocket |

### 管理端口

| 端口 | 服务 | 说明 |
|------|------|------|
| 18083 | HTTP | EMQX Dashboard |
| 18084 | HTTPS | EMQX Dashboard (安全) |
| 5601 | HTTP | Kibana |
| 9200 | HTTP | Elasticsearch |
| 9600 | HTTP | Logstash API |

---

## 数据持久化

所有服务数据存储在 `/root/data/` 目录：

```
/root/data/
├── elk/
│   ├── elasticsearch/      # Elasticsearch 数据
│   ├── logstash/          # Logstash 配置
│   └── kibana/           # Kibana 数据
└── emqx/
    ├── data/             # EMQX 数据
    ├── log/              # EMQX 日志
    └── etc/              # EMQX 配置
```

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
# 所有服务
docker compose -f docker-compose.emqx.yml logs -f

# 仅 EMQX
docker compose -f docker-compose.emqx.yml logs -f emqx

# 仅 Logstash
docker compose -f docker-compose.emqx.yml logs -f logstash
```

### 重启服务

```bash
docker compose -f docker-compose.emqx.yml restart emqx
```

### 进入容器

```bash
# 进入 EMQX
docker exec -it emqx sh

# 进入 Logstash
docker exec -it logstash sh
```

---

## MQTT 客户端连接示例

### Python

```python
import paho.mqtt.client as mqtt

client = mqtt.Client("python_client")
client.connect("localhost", 1883)
client.publish("test/topic", "Hello EMQX")
```

### Node.js

```javascript
const mqtt = require('mqtt');
const client = mqtt.connect('mqtt://localhost:1883');

client.on('connect', () => {
  client.publish('test/topic', 'Hello from Node.js');
});
```

### MQTTX 客户端

下载: https://mqttx.app/zh

配置:
- Host: `localhost`
- Port: `1883`
- Client ID: 任意

---

## 集成到 ELK

### 方案 1: EMQX 规则引擎（推荐）

1. 访问 EMQX Dashboard: http://localhost:18083
2. 进入 `数据桥接` -> `规则`
3. 创建规则：

```sql
SELECT
  topic,
  payload,
  qos,
  clientid,
  username,
  timestamp
FROM "#"
```

4. 添加动作 -> Webhook:
   - URL: `http://logstash:5000/emqx`
   - 方法: POST
   - 内容类型: `application/json`

### 方案 2: Logstash 采集

配置 Logstash 输入：

```ruby
input {
  tcp {
    port => 5001
    codec => json_lines
  }
}
```

---

## 安全建议

### 生产环境配置

1. **修改默认密码**

登录 Dashboard 后修改 admin 密码。

2. **禁用匿名访问**

在 `docker-compose.emqx.yml` 中：
```yaml
environment:
  - EMQX__ALLOW_ANONYMOUS=false
```

3. **启用 TLS/SSL**

```yaml
ports:
  - "8883:8883"  # MQTT over TLS
```

4. **配置认证和授权**

在 Dashboard 中：
- 创建用户和密码
- 设置 ACL 规则限制主题访问

---

## 故障排查

### EMQX 无法连接

```bash
# 检查 EMQX 状态
docker ps | grep emqx

# 查看日志
docker logs emqx

# 测试端口
telnet localhost 1883
```

### 数据未存储到 Elasticsearch

```bash
# 检查 Logstash
docker logs logstash

# 检查 Elasticsearch
curl http://localhost:9200/_cluster/health

# 查看索引
curl http://localhost:9200/_cat/indices
```

### Dashboard 无法访问

```bash
# 检查端口
netstat -tlnp | grep 18083

# 查看日志
docker logs emqx | grep dashboard
```

---

## 性能优化

### EMQX 优化

```yaml
environment:
  # 最大连接数
  - EMQX__LISTENER__TCP__EXTERNAL__MAX_CONNECTIONS=10000

  # 最大消息大小
  - EMQX__MQTT__MAX_PACKET_SIZE=256KB

  # 内存限制
  - EMQX__ZONE__EXTERNAL__MAX_SUBSCRIPTIONS=100
```

### Logstash 优化

```yaml
environment:
  - "LS_JAVA_OPTS=-Xms512m -Xmx512m"
```

### Elasticsearch 优化

```yaml
environment:
  - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
```

---

## 监控

### EMQX 监控

Dashboard -> Overview 查看：
- 连接数
- 消息速率
- 系统资源

### ELK 监控

Kibana -> Dashboard 创建仪表板查看：
- MQTT 消息趋势
- 设备连接状态
- 主题分布

---

## 备份和恢复

### 备份

```bash
# 备份 EMQX
tar -czf emqx-backup-$(date +%Y%m%d).tar.gz /root/data/emqx

# 备份 ELK
tar -czf elk-backup-$(date +%Y%m%d).tar.gz /root/data/elk
```

### 恢复

```bash
# 恢复 EMQX
tar -xzf emqx-backup-YYYYMMDD.tar.gz -C /

# 恢复 ELK
tar -xzf elk-backup-YYYYMMDD.tar.gz -C /
```

---

## 参考资源

- [EMQX 官方文档](https://www.emqx.io/docs/)
- [EMQX Dashboard 使用指南](https://www.emqx.io/docs/zh/dashboard/)
- [MQTT 协议规范](http://mqtt.org/)
- [ELK Stack 文档](https://www.elastic.co/guide/)

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 许可证

MIT License
