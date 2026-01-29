# OneNET MQTT 主题测试结果

## 测试执行时间
2026-01-28

## 测试环境
- MQTT Broker: mqtts.heclouds.com:1883
- 产品 ID: v6IkuqD6vh
- 测试设备: MO (订阅端), MO1 (发送端)

---

## 测试 1: 设备间消息转发测试

### 测试目的
验证不同设备之间能否通过 MQTT 直接互相订阅和接收消息

### 测试方法
- 使用 MO 设备订阅: `$sys/{pid}/MO/thing/#`
- 使用 MO1 设备发送到: `$sys/{pid}/MO1/thing/property/post`

### 测试结果
```
❌ 测试失败：未收到任何消息
```

### 结果分析

**发送端（MO1）:** ✅ 成功
- 连接成功
- 成功发送 4 条测试消息到各种主题
- MQTT 返回码: 0 (成功)

**订阅端（MO):** ❌ 未收到
- 连接成功
- 成功订阅 8 种主题模式（使用 `+` 和 `#` 通配符）
- 但未接收到任何消息

### 结论

**OneNET 平台限制:**
1. 不同设备之间**无法直接**通过 MQTT 互相订阅消息
2. `$sys/{pid}/MO/...` 主题只能接收**发送给 MO 设备**的消息
3. MO1 发送到 `$sys/{pid}/MO1/...` 的消息，**不会转发**给 MO

---

## OneNET 主题订阅规则

### 1. 设备只能订阅自己接收到的主题

```
设备 A: $sys/{pid}/设备A/thing/#    ✓ 可以订阅
设备 A: $sys/{pid}/设备B/thing/#    ✗ 订阅后收不到消息
```

### 2. 消息流向

```
OneNET 平台 → $sys/{pid}/{device-name}/... → 该设备
                 ↑
            消息来源：
            - 设备上报数据
            - 平台下发命令
            - 物模型事件/服务调用
```

### 3. 设备间通信方式

如果需要在设备间通信，需要通过：
1. **OneNET 平台规则引擎**: 设备A → 平台 → 设备B
2. **自定义主题**: 使用非 `$sys` 开头的主题
3. **HTTP API**: 通过 OneNET 的 REST API

---

## 推荐的订阅主题配置

根据 OneNET 官方文档和实际测试，MO 设备应该订阅以下主题：

### 方案 A: 订阅所有物模型和命令（推荐）
```bash
# 覆盖物模型和命令下发
$sys/v6IkuqD6vh/MO/thing/#
$sys/v6IkuqD6vh/MO/cmd/#
```

### 方案 B: 更细粒度订阅
```bash
# 物模型属性
$sys/v6IkuqD6vh/MO/thing/property/#

# 物模型服务调用
$sys/v6IkuqD6vh/MO/thing/service/+/invoke
$sys/v6IkuqD6vh/MO/thing/service/+/invoke_reply

# 命令下发
$sys/v6IkuqD6vh/MO/cmd/request/+
$sys/v6IkuqD6vh/MO/cmd/response/+/accepted
$sys/v6IkuqD6vh/MO/cmd/response/+/rejected
```

---

## ELK MQTT 桥接配置建议

### setup-mqtt.sh 配置
```bash
# 订阅 MO 设备的所有物模型和命令消息
MQTT_TOPICS="\$sys/v6IkuqD6vh/MO/thing/#
,\$sys/v6IkuqD6vh/MO/cmd/#"
```

### 多设备配置
如果有多个设备需要收集数据：
```bash
# 订阅所有设备的消息（但每个设备只能收到发给自己的）
MQTT_TOPICS="\$sys/v6IkuqD6vh/+/thing/#
,\$sys/v6IkuqD6vh/+/cmd/#"
```

---

## 实际应用场景

### 场景 1: MO 设备上报数据
```
MO → $sys/v6IkuqD6vh/MO/thing/property/post
     ↓
MO (订阅端) ✓ 可以收到
```

### 场景 2: 平台向 MO 下发命令
```
平台 → $sys/v6IkuqD6vh/MO/cmd/request/reboot
      ↓
MO (订阅端) ✓ 可以收到
```

### 场景 3: MO1 上报数据，MO 想监听
```
MO1 → $sys/v6IkuqD6vh/MO1/thing/property/post
      ↓
MO (订阅端) ✗ 收不到（平台限制）
```

---

## 测试文件说明

### 已创建的测试脚本

1. **test-mo-listen.py** - 持续监听 MO 设备消息
   ```bash
   python3 mqtt/test-mo-listen.py
   ```
   长期运行，监听 OneNET 平台向 MO 发送的所有消息

2. **test-onenet-standard-topics.py** - 自动化测试
   ```bash
   python3 mqtt/test-onenet-standard-topics.py
   ```
   验证主题格式和通配符（但受平台限制）

3. **test-mo-subscribe.py** - MO 订阅端
   ```bash
   python3 mqtt/test-mo-subscribe.py
   ```
   持续订阅并显示收到的消息

4. **test-send-to-mo.py** - 发送端
   ```bash
   python3 mqtt/test-send-to-mo.py
   ```
   向 MO 发送测试消息（用于配合其他测试）

---

## 如何触发实际消息到 MO

由于设备间无法直接通信，可以通过以下方式测试 MO 的订阅：

### 方法 1: OneNET 控制台
1. 登录 OneNET 平台
2. 进入产品 v6IkuqD6vh
3. 选择设备 MO
4. 点击"下发命令"或"调用服务"

### 方法 2: 使用 REST API
```bash
# 通过 OneNET API 向 MO 下发命令
curl -X POST "https://api.heclouds.com/cmds?device_id=MO" \
  -H "api-key: YOUR_API_KEY" \
  -d '{"cmd": "test"}'
```

### 方法 3: 实际设备
如果 MO 是真实的 IoT 设备，让设备上报数据：
```bash
# ESP32/Arduino 等设备连接后自然会上报数据
```

---

## 总结

### ✅ 已验证
1. ✓ MQTT 连接正常
2. ✓ 主题订阅成功（8 种模式）
3. ✓ 消息发送成功
4. ✓ 通配符 `+` 和 `#` 语法正确

### ❌ 受限制
1. ✗ 设备间无法直接订阅彼此的消息
2. ✗ 需要通过 OneNET 平台作为中转

### 📌 关键发现
- OneNET 的 `$sys` 主题有严格的设备隔离
- ELK MQTT 桥接应该监听**平台下发的消息**，而不是设备间的直接通信
- 实际使用时，应该：
  - 监听设备上报到平台的物模型数据
  - 监听平台下发到设备的命令
  - 使用 OneNET 规则引擎实现设备间转发

---

## 下一步建议

1. **更新 ELK MQTT 配置**
   修改 `mqtt/setup-mqtt.sh`，使用正确的订阅主题

2. **验证真实数据流**
   在有实际设备运行时，使用 `test-mo-listen.py` 监听

3. **设置 OneNET 规则引擎**（如果需要设备间通信）
   - 创建规则: 设备A上报 → 平台 → 转发到设备B
   - 或转发到自定义主题

4. **测试自定义主题**
   评估是否可以使用非 `$sys` 开头的自定义主题实现设备间通信
