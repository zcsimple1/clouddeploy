# ELK 部署指南

ELK 是 Elasticsearch、Logstash、Kibana 的缩写，是一个强大的日志收集、分析和可视化解决方案。

## 架构说明

```
应用容器 (Nginx)
    ↓ 日志
Logstash (日志采集和处理)
    ↓
Elasticsearch (日志存储和索引)
    ↓
Kibana (日志可视化和查询)
```

## 资源要求

- **Elasticsearch**: 最少 1GB 内存（配置为 512MB）
- **Logstash**: 最少 512MB 内存
- **Kibana**: 最少 512MB 内存
- **总计**: 建议至少 4GB 可用内存

## 部署方式

### 方式 1: 仅部署 ELK

```bash
./deploy-elk.sh
```

### 方式 2: 部署所有服务（应用 + ELK）

```bash
./deploy-all.sh
```

## 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Kibana | http://localhost:5601 | 日志可视化界面 |
| Elasticsearch | http://localhost:9200 | 日志存储 API |
| Logstash | http://localhost:9600 | Logstash 监控 |

## 使用 Kibana

### 1. 首次访问

打开 http://localhost:5601

### 2. 创建索引模式

1. 点击左侧菜单 "Management" → "Stack Management"
2. 点击 "Index Patterns" → "Create index pattern"
3. 输入索引模式：`logs-*` 或 `logs-edutool-*`
4. 选择时间字段：`@timestamp`
5. 点击 "Create index pattern"

### 3. 查看日志

1. 点击左侧菜单 "Discover"
2. 选择索引模式
3. 开始查看和分析日志

### 4. 创建仪表板

1. 点击左侧菜单 "Dashboard"
2. 点击 "Create dashboard"
3. 添加各种可视化组件

## 常用命令

```bash
# 查看 ELK 服务状态
docker-compose -f docker-compose.elk.yml ps

# 查看 ELK 日志
docker-compose -f docker-compose.elk.yml logs -f

# 查看 Elasticsearch 状态
curl http://localhost:9200/_cluster/health

# 查看所有索引
curl http://localhost:9200/_cat/indices

# 停止 ELK 服务
docker-compose -f docker-compose.elk.yml down

# 重启 ELK 服务
docker-compose -f docker-compose.elk.yml restart
```

## 配置说明

### 数据存储路径

ELK 数据存储在 `/root/data/elk/` 目录下：

```
/root/data/elk/
├── elasticsearch/    # Elasticsearch 数据
└── logstash/         # Logstash 配置文件
    ├── pipeline/     # Logstash 管道配置
    └── config/       # Logstash 系统配置
```

如需修改存储路径，请编辑 `docker-compose.elk.yml` 文件中的 volumes 配置。

### Logstash 配置

- **配置文件**: `logstash/pipeline/logstash.conf`
- **监听端口**: 5000 (TCP/UDP)
- **输出目标**: Elasticsearch

### Elasticsearch 配置

- **单节点模式**: `discovery.type=single-node`
- **安全设置**: `xpack.security.enabled=false` (开发环境)
- **内存限制**: 512MB

## 轻量级替代方案

如果资源有限，可以考虑以下轻量级替代方案：

### 1. Loki + Grafana
```bash
# 资源占用更少，适合小规模应用
```

### 2. 直接使用 Docker 日志驱动
```bash
# 在 docker-compose.yml 中配置
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 3. 使用云服务
- 腾讯云 CLS
- 阿里云 SLS
- AWS CloudWatch

## 注意事项

1. **首次启动**: Elasticsearch 需要等待 1-2 分钟完全启动
2. **端口冲突**: 确保 9200、5601、9600 端口未被占用
3. **磁盘空间**: Elasticsearch 会占用较多磁盘空间，建议定期清理
4. **生产环境**: 生产环境应启用安全认证和持久化存储

## 故障排查

### Elasticsearch 启动失败
```bash
# 检查日志
docker-compose -f docker-compose.elk.yml logs elasticsearch

# 检查磁盘空间
df -h
```

### Kibana 无法连接 Elasticsearch
```bash
# 等待 Elasticsearch 完全启动
curl http://localhost:9200/_cluster/health
```

### Logstash 无法收集日志
```bash
# 检查配置文件
cat logstash/pipeline/logstash.conf

# 查看 Logstash 日志
docker-compose -f docker-compose.elk.yml logs logstash
```
