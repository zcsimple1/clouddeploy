# OneNET MQTT 主题测试指南

## 测试文件说明

### 1. test-mo-subscribe.py
**MO 设备订阅端**
- 使用 MO 设备订阅各种主题
- 使用 `#` 和 `+` 通配符
- 持续监听并显示收到的消息

**使用方法：**
```bash
python3 mqtt/test-mo-subscribe.py
```

**订阅的主题：**
- `$sys/{pid}/MO/thing/#` - 全部物模型相关主题（多层通配符）
- `$sys/{pid}/MO/thing/property/#` - 物模型属性类
- `$sys/{pid}/MO/thing/service/+/invoke` - 服务调用（单层通配符）
- `$sys/{pid}/MO/thing/service/+/invoke_reply` - 服务调用回复
- `$sys/{pid}/MO/cmd/#` - 数据流命令下发（多层通配符）
- `$sys/{pid}/MO/cmd/request/+` - 命令请求（单层通配符）
- `$sys/{pid}/MO/cmd/response/+/accepted` - 命令响应（单层通配符）
- `$sys/{pid}/MO/cmd/response/+/rejected` - 命令拒绝（单层通配符）

---

### 2. test-send-to-mo.py
**向 MO 发送消息的客户端**
- 使用 MO1 设备发送测试消息
- 发送到各种标准主题格式
- 验证通配符订阅是否生效

**使用方法：**
```bash
python3 mqtt/test-send-to-mo.py
```

**发送的消息类型：**
1. 物模型属性上报: `$sys/{pid}/MO1/thing/property/post`
2. 物模型事件上报: `$sys/{pid}/MO1/thing/event/post`
3. 物模型服务调用回复: `$sys/{pid}/MO1/thing/service/property/set_reply`
4. 命令下发请求: `$sys/{pid}/MO/cmd/request/update`
5. 命令响应 accepted: `$sys/{pid}/MO/cmd/response/accepted/accepted`
6. 自定义数据主题: `$sys/{pid}/MO/custom/data`

---

### 3. test-onenet-standard-topics.py
**完整自动化测试脚本**
- 同时启动订阅端和发送端
- 自动验证主题格式和通配符
- 生成测试报告

**使用方法：**
```bash
python3 mqtt/test-onenet-standard-topics.py
```

---

## 推荐测试流程

### 方案A：手动测试（推荐用于调试）

**终端1 - 启动订阅端：**
```bash
cd /Users/zora/Documents/Work/mygithub/clouddeploy
python3 mqtt/test-mo-subscribe.py
```

**终端2 - 发送消息：**
```bash
cd /Users/zora/Documents/Work/mygithub/clouddeploy
python3 mqtt/test-send-to-mo.py
```

**观察：**
- 终端1 应该显示收到的所有消息
- 检查哪些主题被成功匹配
- 验证通配符是否按预期工作

---

### 方案B：自动化测试

```bash
cd /Users/zora/Documents/Work/mygithub/clouddeploy
python3 mqtt/test-onenet-standard-topics.py
```

脚本会自动：
1. 启动 MO 订阅端
2. 启动 MO1 发送端
3. 发送各种格式的消息
4. 验证订阅端是否收到
5. 生成测试报告

---

## 主题格式说明

### 通配符规则

| 通配符 | 含义 | 示例 |
|--------|------|------|
| `+` | 单层通配符（匹配任意一层） | `$sys/+/MO/thing/#` |
| `#` | 多层通配符（匹配零层或多层） | `$sys/{pid}/MO/thing/#` |

### 标准主题格式

#### 1. 物模型相关主题
```
$sys/{pid}/{device-name}/thing/#
```
- `thing` - 物模型根节点
- `property` - 属性类
- `event` - 事件类
- `service` - 服务类

**示例：**
- `$sys/v6IkuqD6vh/MO/thing/property/post`
- `$sys/v6IkuqD6vh/MO/thing/event/post`
- `$sys/v6IkuqD6vh/MO/thing/service/+/invoke`

#### 2. 物模型属性类
```
$sys/{pid}/{device-name}/thing/property/#
```

**示例：**
- `$sys/v6IkuqD6vh/MO/thing/property/post`
- `$sys/v6IkuqD6vh/MO/thing/property/set_reply`

#### 3. 物模型服务调用类
使用单层通配符 `+`：
```
$sys/{pid}/{device-name}/thing/service/+/invoke
$sys/{pid}/{device-name}/thing/service/+/invoke_reply
```

**示例：**
- `$sys/v6IkuqD6vh/MO/thing/service/property/invoke`
- `$sys/v6IkuqD6vh/MO/thing/service/action/invoke_reply`

#### 4. 数据流命令下发
```
$sys/{pid}/{device-name}/cmd/#
$sys/{pid}/{device-name}/cmd/request/+
$sys/{pid}/{device-name}/cmd/response/+/accepted
$sys/{pid}/{device-name}/cmd/response/+/rejected
```

**示例：**
- `$sys/v6IkuqD6vh/MO/cmd/request/update`
- `$sys/v6IkuqD6vh/MO/cmd/response/cmd123/accepted`

---

## 注意事项

### Token 配置
- **MO 设备**: 使用产品级 Token
  ```
  version=2018-10-31&res=products%2Fv6IkuqD6vh&et=1855626888&method=sha1&sign=xhR6Azo%2BPoFz7Tw0iFA1uMKNXNs%3D
  ```

- **MO1 设备**: 使用设备级 Token
  ```
  version=2018-10-31&res=products%2Fv6IkuqD6vh%2Fdevices%2FMO1&et=1772105871&method=sha1&sign=ZZoc17%2BbrxprIZ7prgo82Y%2FTDG4%3D
  ```

### 常见问题

1. **设备间消息无法接收**
   - 确认 Token 权限（产品级 vs 设备级）
   - 检查主题格式是否正确
   - 确认目标设备在线

2. **通配符不生效**
   - `#` 必须放在主题层级末尾
   - `+` 只能匹配单层

3. **连接失败**
   - 检查网络连接
   - 确认 MQTT Broker 地址和端口
   - 验证 Token 是否过期

---

## 测试结果预期

### 成功场景
- 订阅端收到所有发送的消息
- 通配符正确匹配相应主题
- 消息内容完整无误

### 失败场景
- 未收到消息：检查主题格式或 Token 权限
- 只收到部分消息：检查订阅的主题模式
- 消息格式错误：验证 JSON 格式和字段

---

## 下一步

测试通过后，可以将这些主题配置应用到 ELK MQTT 桥接服务：
- 编辑 `mqtt/setup-mqtt.sh`
- 修改 `MQTT_TOPICS` 配置
- 重启服务

示例：
```bash
# 订阅全部物模型和命令主题
MQTT_TOPICS="\$sys/v6IkuqD6vh/MO/thing/#,\$sys/v6IkuqD6vh/MO/cmd/#"
```
