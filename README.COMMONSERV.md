# CommonServ 部署指南

## 快速开始

### 部署所有服务（包括 CommonServ）

```bash
cd /Users/zora/Documents/Work/mygithub/clouddeploy
docker-compose up -d --build
```

### 仅部署 CommonServ

```bash
docker-compose up -d commonserv
```

## 服务配置

### Docker Compose 配置

CommonServ 使用以下配置：

```yaml
commonserv:
  build:
    context: ../commonserv
    dockerfile: Dockerfile
  container_name: commonserv
  restart: unless-stopped
  environment:
    - PYTHONUNBUFFERED=1
  volumes:
    - ../commonserv:/app
    - ./logs:/var/log/commonserv
  ports:
    - "8000:8000"
  networks:
    - elk
```

### 配置说明

- **挂载卷**: `../commonserv:/app` - 支持代码热更新
- **日志目录**: `./logs:/var/log/commonserv` - 日志集中存储
- **网络**: `elk` - 与 ELK 集成
- **端口**: 8000 - FastAPI 服务端口

## 访问服务

### 通过 Nginx 反向代理（推荐）

- **API 服务**: http://localhost:8080/api/
- **API 文档**: http://localhost:8080/api/docs
- **OpenAPI**: http://localhost:8080/api/openapi.json

### 直接访问

- **API 服务**: http://localhost:8000/
- **API 文档**: http://localhost:8000/docs

## 测试服务

### 自动化测试

```bash
./test-commonserv.sh
```

### 手动测试

```bash
# 测试根路径
curl http://localhost:8080/api/

# 测试健康检查
curl http://localhost:8080/api/health

# 测试 MQTT Token 服务
curl http://localhost:8080/api/mqtt/onenet/v1/config
```

## 常用命令

```bash
# 查看 CommonServ 日志
docker-compose logs -f commonserv

# 重启 CommonServ
docker-compose restart commonserv

# 进入容器
docker-compose exec commonserv bash

# 查看容器状态
docker-compose ps commonserv
```

## 自动更新

CommonServ 已集成到自动更新机制中：

- 每 5 分钟自动检查代码更新
- 如果检测到更新，自动拉取并重启容器
- 查看更新日志：`tail -f /tmp/auto-update.log`

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs commonserv

# 检查端口占用
lsof -i :8000
```

### Nginx 代理失败

```bash
# 检查 Nginx 配置
docker-compose logs nginx

# 验证 CommonServ 是否正常运行
curl http://localhost:8000/
```

### 代码更新未生效

```bash
# 手动重启容器
docker-compose restart commonserv

# 检查挂载是否正确
docker-compose exec commonserv ls -la /app
```

## API 端点

### 基础端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务列表和信息 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger UI 文档 |
| `/openapi.json` | GET | OpenAPI 规范 |

### MQTT Token 服务

| 端点 | 方法 | 描述 |
|------|------|------|
| `/mqtt/onenet/v1/config` | GET | OneNET 配置信息 |
| `/mqtt/onenet/v1/token/product` | GET | 产品级 Token |
| `/mqtt/onenet/v1/token/device/mo` | GET | MO 设备 Token |
| `/mqtt/onenet/v1/token/device/mo1` | GET | MO1 设备 Token |

## 与 ELK 集成

CommonServ 的日志会自动发送到 Logstash：

1. 日志文件存储在 `./logs/commonserv/`
2. Logstash 采集并索引到 Elasticsearch
3. 通过 Kibana 查询和分析日志

## 注意事项

1. **代码热更新**: 由于使用卷挂载，修改代码会立即生效
2. **依赖管理**: 修改 `requirements.txt` 后需要重新构建镜像
3. **日志轮转**: 日志文件会自动轮转，避免占用过多磁盘空间
4. **网络隔离**: CommonServ 运行在 `elk` 网络中，可以访问 ELK 服务
