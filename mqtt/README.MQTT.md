# ELK + OneNET MQTT 集成说明

## 配置说明

### MQTT 连接信息

- **Host**: mqtts.heclouds.com
- **Port**: 1883
- **Product ID**: v6IkuqD6vh
- **Device ID**: MO
- **Username**: v6IkuqD6vh
- **Password**: version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D

### 订阅主题

当前配置订阅所有主题 `#`，可根据需要修改 `logstash/pipeline/logstash.conf`：

```conf
topics => ["#"]  # 订阅所有主题
# 或指定主题
# topics => ["sys/#", "property/#"]
```

## 部署步骤

### 1. 首次部署

```bash
# 创建 Logstash 配置目录
sudo mkdir -p /root/data/elk/logstash/pipeline
sudo mkdir -p /root/data/elk/logstash/config

# 复制配置文件到外部目录
cp -r logstash/pipeline/* /root/data/elk/logstash/pipeline/
cp -r logstash/config/* /root/data/elk/logstash/config/

# 设置权限
sudo chown -R 1000:1000 /root/data/elk/logstash

# 构建并启动 ELK
docker-compose -f docker-compose.elk.yml up -d --build
```

### 2. 更新部署

```bash
# 停止旧容器
docker-compose -f docker-compose.elk.yml down

# 拉取最新配置
git pull

# 重新构建并启动（更新 MQTT 配置）
docker-compose -f docker-compose.elk.yml up -d --build
```

## 查看数据

### 1. Kibana 中查看

1. 访问 http://101.35.135.63:5601
2. 进入 Stack Management → Index Patterns
3. 创建索引模式：`logs-onenet-*`
4. 选择时间字段：`@timestamp`
5. 在 Discover 中查看 MQTT 数据

### 2. 查询示例

```json
// 查询特定设备
{
  "query": {
    "match": {
      "device_id": "MO"
    }
  }
}

// 查询时间范围内的数据
{
  "query": {
    "range": {
      "@timestamp": {
        "gte": "now-1h"
      }
    }
  }
}
```

## 调试

### 查看 Logstash 日志

```bash
# 实时查看日志
docker logs -f logstash

# 查看 MQTT 连接错误
docker logs logstash | grep -i mqtt
```

### 测试 MQTT 连接

```bash
# 进入 Logstash 容器
docker exec -it logstash bash

# 测试连接
telnet mqtts.heclouds.com 1883
```

## 常见问题

### 1. MQTT 连接失败

- 检查密码是否过期（et 参数是过期时间戳）
- 检查网络连通性：`ping mqtts.heclouds.com`
- 查看 Logstash 日志确认错误信息

### 2. 数据未接收

- 确认设备已发布消息到 OneNET
- 检查 Logstash 是否成功订阅主题
- 在 Kibana 中检查索引是否创建

### 3. 密码过期

密码中的 `et=1855626888` 是过期时间戳，需要定期更新：
1. 重新生成 Token
2. 更新 `logstash/pipeline/logstash.conf` 中的 password
3. 重启 Logstash：`docker-compose -f docker-compose.elk.yml restart logstash`

## 数据存储

所有数据存储在 `/root/data/elk/` 目录下：

- **Elasticsearch**: `/root/data/elk/elasticsearch/`
- **Logstash 配置**: `/root/data/elk/logstash/`
- **Kibana 数据**: `/root/data/elk/kibana/data/`

升级或重建容器不会丢失数据。
