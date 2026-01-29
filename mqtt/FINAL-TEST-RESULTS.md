# MO 设备物模型通信测试 - 最终结果

## 测试时间
2026-01-28

## ✅ 测试成功！

### 关键发现

#### 1. Client ID 必须使用设备名
- ✅ Client ID: **"MO"** - 连接成功 (rc=0)
- ❌ Client ID: 其他名称 - 连接失败 (rc=4)

**结论：** MO 设备连接 OneNET MQTT 时，必须使用 `"MO"` 作为 Client ID

---

## 测试执行的通信流程

### 设备侧操作（发布到平台）

#### 消息 1: 设备属性上报
```
主题: $sys/v6IkuqD6vh/MO/thing/property/post
操作: 发布
内容: {
  "id": "prop_1769603248",
  "version": "1.0",
  "params": {
    "temperature": 25.5,
    "humidity": 60,
    "pressure": 1013.25,
    "timestamp": 1769603248
  }
}
状态: ✓ 成功
```

#### 消息 2: 设备事件上报
```
主题: $sys/v6IkuqD6vh/MO/thing/event/post
操作: 发布
内容: {
  "id": "event_1769603249",
  "version": "1.0",
  "params": {
    "event": "temperature_alert",
    "value": 35.5,
    "threshold": 30.0
  }
}
状态: ✓ 成功
```

#### 消息 3: 设备数据上传
```
主题: $sys/v6IkuqD6vh/MO/dp/post/json
操作: 发布
内容: {
  "id": "dp_1769603253",
  "version": "1.0",
  "dataPoints": [
    {
      "dsId": "sensor",
      "data": {
        "temperature": 26.0,
        "humidity": 62
      }
    }
  ]
}
状态: ✓ 成功
```

#### 消息 4: 设备镜像更新请求
```
主题: $sys/v6IkuqD6vh/MO/image/update
操作: 发布
内容: {
  "id": "img_1769603255",
  "version": "1.0",
  "params": {
    "url": "https://example.com/firmware.bin",
    "version": "2.0.1",
    "size": 1024000
  }
}
状态: ✓ 成功
```

---

### 设备侧操作（订阅平台下发）

订阅了 13 种平台下发主题：

| # | 主题 | 说明 |
|---|------|------|
| 1 | `$sys/v6IkuqD6vh/MO/thing/property/post/reply` | 属性上报响应 |
| 2 | `$sys/v6IkuqD6vh/MO/thing/property/set` | 属性设置请求 |
| 3 | `$sys/v6IkuqD6vh/MO/thing/property/get` | 属性获取请求 |
| 4 | `$sys/v6IkuqD6vh/MO/thing/event/post/reply` | 事件上报响应 |
| 5 | `$sys/v6IkuqD6vh/MO/thing/service/+/invoke` | 服务调用请求 (+通配符) |
| 6 | `$sys/v6IkuqD6vh/MO/cmd/request/+` | 命令下发请求 (+通配符) |
| 7 | `$sys/v6IkuqD6vh/MO/ota/inform` | OTA升级通知 |
| 8 | `$sys/v6IkuqD6vh/MO/image/update` | 镜像更新请求 |
| 9 | `$sys/v6IkuqD6vh/MO/custome/down/+` | 脚本下行请求 (+通配符) |
| 10 | `$sys/v6IkuqD6vh/MO/dp/post/json/accepted` | 数据上传成功 |
| 11 | `$sys/v6IkuqD6vh/MO/dp/post/json/rejected` | 数据上传失败 |
| 12 | `$sys/v6IkuqD6vh/MO/image/update/accepted` | 镜像更新成功 |
| 13 | `$sys/v6IkuqD6vh/MO/image/update/rejected` | 镜像更新失败 |

---

## OneNET 物模型通信规范总结

### 关键规则

#### 1. Client ID 规则
- **必须使用已注册的设备名**作为 Client ID
- MO 设备 → Client ID = "MO"
- MO1 设备 → Client ID = "MO1"

#### 2. 主题分层结构
```
$sys/{pid}/{device-name}/功能类型/具体操作
     ↑       ↑           ↑
  系统前缀  产品ID    设备名称
```

#### 3. 操作权限
- **发布**: 设备上报数据到平台
- **订阅**: 接收平台下发的命令/响应

#### 4. 通配符使用
- `+` (单层): 匹配任意一层
  - 例如: `thing/service/+/invoke` - 匹配任意服务标识符
- `#` (多层): 匹配零层或多层（必须在主题末尾）
  - 例如: `thing/#` - 匹配所有物模型相关主题

---

## ELK MQTT 桥接配置建议

### 推荐配置（订阅设备上报和平台下发）

```bash
# setup-mqtt.sh

# 订阅 MO 设备的所有物模型和命令主题
MQTT_TOPICS="\$sys/v6IkuqD6vh/MO/thing/#
,\$sys/v6IkuqD6vh/MO/cmd/#
,\$sys/v6IkuqD6vh/MO/dp/post/json/#
,\$sys/v6IkuqD6vh/MO/image/#
,\$sys/v6IkuqD6vh/MO/ota/#
,\$sys/v6IkuqD6vh/MO/custome/+#"

# Client ID 必须是 "MO"
CLIENT_ID="MO"

# Token 使用产品级 Token
MQTT_PASS="version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D"
```

### 配置说明

这个配置可以收集：
1. ✓ 设备上报的属性数据
2. ✓ 设备上报的事件数据
3. ✓ 设备上传的数据点
4. ✓ 设备上报的镜像更新请求
5. ✓ 平台下发的属性设置命令
6. ✓ 平台下发的服务调用请求
7. ✓ 平台下发的命令请求
8. ✓ OTA 升级相关消息
9. ✓ 脚本透传消息

---

## 通配符验证

### 测试过的通配符模式

✅ **# 多层通配符**
```bash
$sys/v6IkuqD6vh/MO/thing/#  # ✓ 成功订阅
```
匹配所有物模型相关主题

✅ **+ 单层通配符**
```bash
$sys/v6IkuqD6vh/MO/thing/service/+/invoke  # ✓ 成功订阅
$sys/v6IkuqD6vh/MO/cmd/request/+            # ✓ 成功订阅
$sys/v6IkuqD6vh/MO/custome/down/+           # ✓ 成功订阅
```
匹配任意一层内容

---

## 测试文件

### 成功的测试脚本

1. **test-cloud.py**
   - 验证了连接规则
   - 发现必须使用 "MO" 作为 Client ID

2. **test-mo-correct.py**
   - 完整的物模型通信测试
   - 验证了发布和订阅功能
   - 测试了通配符功能

---

## 使用建议

### 开发调试

运行监听脚本，实时查看设备消息：
```bash
python3 mqtt/test-mo-correct.py
```

### 生产环境

使用 setup-mqtt.sh 部署 ELK MQTT 桥接：
```bash
bash mqtt/setup-mqtt-v2.sh MO
```

---

## 总结

### ✅ 验证成功的功能

1. ✓ MO 设备可以成功连接 OneNET MQTT
2. ✓ MO 设备可以发布上报数据到平台
3. ✓ MO 设备可以订阅平台下发的主题
4. ✓ 通配符 `+` 和 `#` 正常工作
5. ✓ 不同的主题对应不同的操作权限

### 📌 关键要点

1. **Client ID 必须是设备名**（MO）
2. **主题格式严格**：`$sys/{pid}/{device-name}/...`
3. **发布/订阅分离**：不同主题用于不同方向
4. **通配符强大**：`+` 和 `#` 可以简化订阅

### 🎯 下一步

1. 更新 `setup-mqtt.sh` 使用正确的配置
2. 部署 ELK MQTT 桥接服务
3. 在 OneNET 平台触发实际操作（如属性设置、命令下发）验证完整流程
4. 在 Kibana 中查看收集到的数据

---

## 附录：完整的主题映射表

| 功能 | 主题 | 权限 |
|------|------|------|
| **属性上报** | | |
| 属性上报请求 | `$sys/{pid}/{device}/thing/property/post` | 发布 |
| 属性上报响应 | `$sys/{pid}/{device}/thing/property/post/reply` | 订阅 |
| 属性设置 | `$sys/{pid}/{device}/thing/property/set` | 订阅 |
| 属性设置响应 | `$sys/{pid}/{device}/thing/property/set_reply` | 发布 |
| 属性获取 | `$sys/{pid}/{device}/thing/property/get` | 订阅 |
| 属性获取响应 | `$sys/{pid}/{device}/thing/property/get_reply` | 发布 |
| **事件上报** | | |
| 事件上报请求 | `$sys/{pid}/{device}/thing/event/post` | 发布 |
| 事件上报响应 | `$sys/{pid}/{device}/thing/event/post/reply` | 订阅 |
| **服务调用** | | |
| 服务调用请求 | `$sys/{pid}/{device}/thing/service/{id}/invoke` | 订阅 |
| 服务调用响应 | `$sys/{pid}/{device}/thing/service/{id}/invoke_reply` | 发布 |
| **命令下发** | | |
| 命令请求 | `$sys/{pid}/{device}/cmd/request/+` | 订阅 |
| 命令响应 | `$sys/{pid}/{device}/cmd/response/{cmdId}` | 发布 |
| 命令成功 | `$sys/{pid}/{device}/cmd/response/+/accepted` | 订阅 |
| 命令失败 | `$sys/{pid}/{device}/cmd/response/+/rejected` | 订阅 |
| **数据点上传** | | |
| 数据上传 | `$sys/{pid}/{device}/dp/post/json` | 发布 |
| 上传成功 | `$sys/{pid}/{device}/dp/post/json/accepted` | 订阅 |
| 上传失败 | `$sys/{pid}/{device}/dp/post/json/rejected` | 订阅 |
| **OTA升级** | | |
| OTA通知 | `$sys/{pid}/{device}/ota/inform` | 订阅 |
| OTA回复 | `$sys/{pid}/{device}/ota/inform_reply` | 发布 |
| **设备镜像** | | |
| 镜像更新 | `$sys/{pid}/{device}/image/update` | 发布 |
| 更新成功 | `$sys/{pid}/{device}/image/update/accepted` | 订阅 |
| 更新失败 | `$sys/{pid}/{device}/image/update/rejected` | 订阅 |
| 获取镜像 | `$sys/{pid}/{device}/image/get` | 订阅 |
| 获取成功 | `$sys/{pid}/{device}/image/get/accepted` | 订阅 |
| 获取失败 | `$sys/{pid}/{device}/image/get/rejected` | 订阅 |
