# MO 设备订阅功能测试 - 完整结果

## 测试日期
2026-01-28

---

## 重要发现：OneNET 订阅限制

### ❌ 测试结果

**订阅功能验证：无法通过模拟完成**

#### 测试 1: 设备订阅主题
```
✓ 连接成功 (rc=0)
✓ 成功订阅 13 种平台下发主题
```

订阅的主题包括：
- `$sys/v6IkuqD6vh/MO/thing/property/set` - 属性设置请求
- `$sys/v6IkuqD6vh/MO/thing/property/get` - 属性获取请求
- `$sys/v6IkuqD6vh/MO/thing/service/+/invoke` - 服务调用请求
- `$sys/v6IkuqD6vh/MO/cmd/request/+` - 命令下发请求
- `$sys/v6IkuqD6vh/MO/ota/inform` - OTA升级通知
- 等等...

#### 测试 2: 模拟平台下发消息
```
✗ 发布失败（所有消息）
```

尝试发布的消息：
1. 属性设置请求 - ✗ 失败
2. 命令下发请求 - ✗ 失败
3. 服务调用请求 - ✗ 失败
4. 属性上报响应 - ✗ 失败
5. 数据上传成功响应 - ✗ 失败

---

## OneNET 平台限制说明

### 1. 主题发布权限

OneNET 对 `$sys` 系统主题有严格的发布权限控制：

| 主题类型 | 发布权限 | 说明 |
|---------|---------|------|
| 设备上报请求 | 设备 | `thing/property/post`, `thing/event/post`, `dp/post/json` 等 |
| 平台响应/命令 | **平台** | `thing/property/post/reply`, `thing/property/set`, `cmd/request/*` 等 |
| 设备响应 | 设备 | `thing/property/set_reply`, `cmd/response/*` 等 |

**关键限制：**
- ❌ 设备**无法**发布到"平台专用"主题
- ❌ 无法通过脚本模拟平台下发消息
- ✅ 只有 OneNET 平台服务器才能发布这些主题

### 2. 设备能做什么

#### ✅ 设备可以发布的主题

```
1. 属性上报
   $sys/{pid}/{device}/thing/property/post

2. 事件上报
   $sys/{pid}/{device}/thing/event/post

3. 数据点上传
   $sys/{pid}/{device}/dp/post/json

4. 属性设置响应
   $sys/{pid}/{device}/thing/property/set_reply

5. 服务调用响应
   $sys/{pid}/{device}/thing/service/{id}/invoke_reply

6. 命令响应
   $sys/{pid}/{device}/cmd/response/{cmdId}

7. OTA升级回复
   $sys/{pid}/{device}/ota/inform_reply

8. 镜像更新
   $sys/{pid}/{device}/image/update

9. 脚本数据上行
   $sys/{pid}/{device}/custome/up
```

#### ✅ 设备可以订阅的主题

```
1. 属性上报响应
   $sys/{pid}/{device}/thing/property/post/reply

2. 属性设置请求（平台下发）
   $sys/{pid}/{device}/thing/property/set

3. 属性获取请求（平台下发）
   $sys/{pid}/{device}/thing/property/get

4. 事件上报响应
   $sys/{pid}/{device}/thing/event/post/reply

5. 服务调用请求（平台下发）
   $sys/{pid}/{device}/thing/service/+/invoke

6. 命令下发请求（平台下发）
   $sys/{pid}/{device}/cmd/request/+

7. OTA升级通知（平台下发）
   $sys/{pid}/{device}/ota/inform

8. 镜像更新请求（平台下发）
   $sys/{pid}/{device}/image/update

9. 数据上传响应
   $sys/{pid}/{device}/dp/post/json/accepted
   $sys/{pid}/{device}/dp/post/json/rejected

10. 镜像更新响应
    $sys/{pid}/{device}/image/update/accepted
    $sys/{pid}/{device}/image/update/rejected

11. 脚本数据下行（平台下发）
    $sys/{pid}/{device}/custome/down/+
```

---

## 如何真正测试订阅功能

### 方案 1: 通过 OneNET 控制台触发

1. 登录 OneNET 平台
2. 进入产品 v6IkuqD6vh
3. 选择设备 MO
4. 执行以下操作：
   - **属性设置**：设置设备属性
   - **命令下发**：发送同步命令
   - **服务调用**：调用设备服务
   - **OTA升级**：推送固件更新

这些操作会触发平台向设备发送消息。

### 方案 2: 使用 OneNET API

通过 OneNET REST API 触发平台操作：

```bash
# 下发命令到设备
curl -X POST "https://api.heclouds.com/cmds?device_id=MO" \
  -H "api-key: YOUR_API_KEY" \
  -d '{
    "cmd": "reboot",
    "timeout": 5000
  }'
```

### 方案 3: 使用真实设备

如果 MO 是真实的 IoT 设备：
1. 让设备连接到 OneNET
2. 通过控制台或 API 向 MO 下发命令
3. 运行订阅脚本监听消息

---

## ELK MQTT 桥接的实际使用场景

基于测试结果，ELK MQTT 桥接应该用于：

### 场景 A: 监听设备上报数据（推荐）

```bash
# 订阅设备主动上报的主题
$sys/v6IkuqD6vh/MO/thing/property/post
$sys/v6IkuqD6vh/MO/thing/event/post
$sys/v6IkuqD6vh/MO/dp/post/json
```

**优点：**
- ✓ 设备持续上报，有源源不断的数据
- ✓ 不依赖平台主动触发
- ✓ 适合实时监控和日志收集

### 场景 B: 监听平台下发的消息

```bash
# 订阅平台下发的主题
$sys/v6IkuqD6vh/MO/thing/property/set
$sys/v6IkuqD6vh/MO/cmd/request/+
$sys/v6IkuqD6vh/MO/thing/service/+/invoke
```

**注意：**
- ⚠️ 只有在平台主动下发时才有消息
- ⚠️ 消息频率取决于操作频率
- ⚠️ 适合审计和命令追踪

### 场景 C: 监听完整通信（推荐）

```bash
# 订阅所有设备相关的消息
$sys/v6IkuqD6vh/MO/thing/#
$sys/v6IkuqD6vh/MO/cmd/#
$sys/v6IkuqD6vh/MO/dp/#
$sys/v6IkuqD6vh/MO/image/#
$sys/v6IkuqD6vh/MO/ota/#
$sys/v6IkuqD6vh/MO/custome/#
```

**优点：**
- ✓ 捕获完整的设备-平台通信
- ✓ 适合全面的监控和调试
- ✓ 记录所有交互日志

---

## 实际验证订阅功能的方法

### 推荐流程

#### 步骤 1: 启动监听脚本

```bash
cd /Users/zora/Documents/Work/mygithub/clouddeploy
python3 mqtt/test-mo-listen.py
```

#### 步骤 2: 在 OneNET 平台执行操作

1. **设置设备属性**
   - 登录 https://open.iot.10086.cn/
   - 进入设备详情
   - 点击"设备属性"
   - 修改属性值并提交

2. **下发命令**
   - 点击"设备命令"
   - 选择同步命令
   - 输入命令内容
   - 点击发送

3. **调用服务**
   - 点击"设备服务"
   - 选择要调用的服务
   - 填写参数
   - 点击调用

#### 步骤 3: 观察监听脚本输出

如果一切正常，应该能看到类似这样的输出：

```
======================================================================
[消息 #1] 收到于 2.3 秒后
======================================================================
  主题: $sys/v6IkuqD6vh/MO/thing/property/set
  QoS: 1 | 保留: false

  内容:
  {
    "id": "123456",
    "version": "1.0",
    "params": {
      "temperature": 25.0
    },
    "method": "thing.service.property.set"
  }
======================================================================
```

---

## 测试总结

### ✅ 验证成功的功能

1. ✓ MO 设备可以连接 OneNET MQTT (Client ID = "MO")
2. ✓ MO 设备可以订阅多种平台下发主题
3. ✓ MO 设备可以发布设备上报主题
4. ✓ 通配符 `+` 和 `#` 功能正常

### ⚠️ 发现的限制

1. ❌ 设备无法发布到"平台专用"主题
2. ❌ 无法通过脚本模拟平台下发消息
3. ⚠️ 订阅功能需要实际的平台操作触发

### 📌 结论

**订阅功能本身是正常的**，但需要：
- 通过 OneNET 控制台触发平台操作
- 通过 OneNET API 调用平台接口
- 或使用真实设备和真实操作

**设备上报功能完全可用**，ELK MQTT 桥接应该优先订阅设备上报的主题，这样可以持续收集数据。

---

## 建议的 ELK MQTT 配置

```bash
# setup-mqtt.sh

# Client ID 必须是 "MO"
CLIENT_ID="MO"

# 订阅所有设备相关的主题（包括上报和下发）
MQTT_TOPICS="\$sys/v6IkuqD6vh/MO/thing/#
,\$sys/v6IkuqD6vh/MO/cmd/#
,\$sys/v6IkuqD6vh/MO/dp/#
,\$sys/v6IkuqD6vh/MO/image/#
,\$sys/v6IkuqD6vh/MO/ota/#
,\$sys/v6IkuqD6vh/MO/custome/#"

# Token 使用产品级 Token
MQTT_PASS="version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
```

这个配置会：
- ✓ 收集所有设备上报的数据
- ✓ 监听所有平台下发的命令
- ✓ 实现完整的通信审计
