# CloudDeploy - 云部署管理

一个用于管理多个 Web 应用云部署的项目，支持自动更新、日志监控等功能。

## 项目结构

本项目管理以下应用的部署：
- **edutool**：中小学每日一练系统
- **zcgames**：游戏项目
- **webtool**：Web 工具项目
- **clouddeploy**：部署管理（当前项目）

## 目录结构要求

```
~/workspace/
├── zcgames/          # 游戏项目
├── edutool/          # 教育工具项目
├── webtool/          # Web 工具项目
└── clouddeploy/      # 当前项目
    ├── docker-compose.yml
    ├── docker-compose.elk.yml
    ├── nginx.conf
    ├── logstash/
    ├── pull-all.sh
    ├── deploy.sh
    ├── status.sh
    ├── deploy-elk.sh
    ├── deploy-all.sh
    ├── check-and-update.sh
    ├── setup-auto-update.sh
    ├── stop-auto-update.sh
    └── README.ELK.md
```

## 快速开始

### 步骤 1: 确保目录结构正确

确保你的目录结构如上所示，所有项目在同一级目录。

### 步骤 2: 进入 clouddeploy 目录

```bash
cd ~/workspace/clouddeploy
```

### 步骤 3: 首次部署

```bash
# 一键部署所有服务（应用 + ELK）
./deploy-all.sh

# 或仅部署应用服务
./deploy.sh
```

### 步骤 4: 启动自动更新

```bash
./setup-auto-update.sh
```

这样每 5 分钟会自动检查所有项目（包括 clouddeploy 自身）的代码更新。

### 步骤 5: 访问项目

打开浏览器访问：
- **首页**: http://localhost:8080/
- **ZCGames**: http://localhost:8080/zcgames/
- **EduTool**: http://localhost:8080/edutool/
- **WebTool**: http://localhost:8080/webtool/

## 脚本说明

| 脚本 | 功能 |
|------|------|
| `deploy.sh` | 一键部署应用服务（拉取代码 + 构建 + 启动） |
| `deploy-all.sh` | 一键部署所有服务（应用 + ELK） |
| `deploy-elk.sh` | 部署 ELK 堆栈 |
| `pull-all.sh` | 拉取所有项目最新代码（包括 clouddeploy 自身） |
| `status.sh` | 查看所有项目的 Git 状态 |
| `check-and-update.sh` | 检测代码更新并自动部署 |
| `setup-auto-update.sh` | 设置自动更新服务（每5分钟） |
| `stop-auto-update.sh` | 停止自动更新服务 |

## 自动更新机制

clouddeploy 会自动检测以下项目的代码更新：
1. **zcgames** - 如果有更新，自动拉取并重启容器
2. **edutool** - 如果有更新，自动拉取并重启容器
3. **webtool** - 如果有更新，自动拉取并重启容器
4. **clouddeploy 自身** - 如果有更新，自动拉取、重新构建并重启容器

### 工作流程

```
每 5 分钟检查一次
    ↓
对比本地和远程 commit ID
    ↓
如果检测到更新：
    - 拉取所有项目最新代码
    - 如果是 clouddeploy 配置更新：重新构建并启动
    - 如果仅是项目代码更新：仅重启容器
    - 记录更新日志
```

## 常用命令

### 应用服务

```bash
# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down

# 重启容器
docker-compose restart

# 重新构建并启动
docker-compose up -d --build
```

### ELK 服务

```bash
# 查看 ELK 状态
docker-compose -f docker-compose.elk.yml ps

# 查看 ELK 日志
docker-compose -f docker-compose.elk.yml logs -f

# 停止 ELK
docker-compose -f docker-compose.elk.yml down
```

### 自动更新

```bash
# 查看自动更新日志
tail -f /tmp/clouddeploy-auto-update.log
tail -f /tmp/auto-update.log

# 停止自动更新
./stop-auto-update.sh
```

### 项目管理

```bash
# 手动拉取代码
./pull-all.sh

# 查看项目状态
./status.sh
```

## 常用操作速查

| 操作 | 命令 |
|------|------|
| 查看自动更新日志 | `tail -f /tmp/clouddeploy-auto-update.log` |
| 手动拉取代码 | `./pull-all.sh` |
| 查看项目状态 | `./status.sh` |
| 重启容器 | `docker-compose restart` |
| 停止自动更新 | `./stop-auto-update.sh` |
| 停止所有服务 | `docker-compose down` && `docker-compose -f docker-compose.elk.yml down` |

## ELK 日志管理

详细信息请参考 [README.ELK.md](README.ELK.md)

### 访问地址

- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Logstash**: http://localhost:9600

## 特点

- ✅ 统一管理多个项目的部署
- ✅ 自动检测并更新所有项目代码
- ✅ clouddeploy 自身配置更新自动重新构建
- ✅ 支持 ELK 日志分析
- ✅ 简化的部署脚本
- ✅ 详细的日志记录

## 注意事项

- 确保所有项目在同一级目录
- 确保端口 8080、9200、5601、9600 未被占用
- ELK 需要至少 4GB 可用内存
- 首次部署需要构建 Docker 镜像，可能需要较长时间

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker-compose logs -f

# 检查端口占用
lsof -i :8080
```

### 自动更新不工作

```bash
# 检查 launchd 服务
launchctl list | grep clouddeploy

# 查看错误日志
cat /tmp/clouddeploy-auto-update-error.log
```

### ELK 无法启动

```bash
# 检查 ELK 日志
docker-compose -f docker-compose.elk.yml logs -f

# 检查磁盘空间
df -h
```
