# Kibana 可视化图表手动创建指南

由于 Dashboard ndjson 格式复杂且兼容性问题，推荐手动创建可视化图表并组合成 Dashboard。

## 步骤 1：创建 Data View

1. 进入 Stack Management → Data Views
2. 点击 "Create data view"
3. Name: `logs-onenet`
4. Index pattern: `logs-onenet-*`
5. 时间字段: `@timestamp`
6. 保存

## 步骤 2：创建可视化图表

### 1. 设备状态总览 Dashboard

**环境温度 Metric:**
- Visualize Library → Create visualization → Metric
- Data view: `logs-onenet`
- Metric: Average `data.params.temp.value`
- 查询条件: `data.params.temp.value: *`

**环境湿度 Metric:**
- Metric: Average `data.params.humi.value`

**温度趋势 Line Chart:**
- Visualize → Create visualization → Line chart
- X轴: Date histogram `@timestamp`
- Y轴: Average `data.params.temp.value`
- 保存: "温度趋势"

### 2. 水箱监控 Dashboard

**冷水池温度 Gauge:**
- Visualize → Create visualization → Gauge
- Metric: Average `data.params.COLD_TANK_TEMP_NTC_C.value`
- Min: 0, Max: 100
- 保存: "冷水池温度"

**热水池温度 Gauge:**
- Metric: Average `data.params.HOT_TANK_TEMP_NTC_C.value`
- 保存: "热水池温度"

**净水池温度 Gauge:**
- Metric: Average `data.params.PURE_TANK_TEMP_NTC_C.value`
- 保存: "净水池温度"

### 3. 温度监控 Dashboard

**炉面温度 Line Chart:**
- Visualize → Create visualization → Line chart
- X轴: Date histogram `@timestamp`
- Y轴: Average `data.params.AT.value`
- 保存: "炉面温度"

**入水温度 Line Chart:**
- X轴: Date histogram `@timestamp`
- Y轴: Average `data.params.INLET_TEMP_1_C.value`
- 保存: "入水温度"

**出水温度 Line Chart:**
- Y轴: Average `data.params.OUTLET_TEMP_1_C.value`
- 保存: "出水温度"

### 4. 水泵监控 Dashboard

**水泵1 电流 Gauge:**
- Visualize → Create visualization → Gauge
- Metric: Average `data.params.PUMP_1_A.value`
- 保存: "水泵1 电流"

**水泵1 功率 Gauge:**
- Metric: Average `data.params.PUMP_1_P.value`
- 保存: "水泵1 功率"

**水泵电流趋势 Line Chart:**
- Visualize → Create visualization → Line chart
- X轴: Date histogram `@timestamp`
- Y轴: Average `data.params.PUMP_1_A.value`
- 保存: "水泵电流趋势"

### 5. 发热管监控 Dashboard

**发热管1 功率 Gauge:**
- Visualize → Create visualization → Gauge
- Metric: Average `data.params.HEATER_1_POWER_W.value`
- 保存: "发热管1 功率"

**发热管功率趋势 Line Chart:**
- Visualize → Create visualization → Line chart
- X轴: Date histogram `@timestamp`
- Y轴: Average `data.params.HEATER_1_POWER_W.value`
- 保存: "发热管功率趋势"

### 6. 流量监控 Dashboard

**流量计1 Gauge:**
- Visualize → Create visualization → Gauge
- Metric: Average `data.params.FLOW_RATE_1_PURE_TANK.value`
- 保存: "流量计1"

**流量趋势 Line Chart:**
- Visualize → Create visualization → Line chart
- X轴: Date histogram `@timestamp`
- Y轴: Average `data.params.FLOW_RATE_1_PURE_TANK.value`
- 保存: "流量趋势"

### 7. 其他设备 Dashboard

**TDS 值 Metric:**
- Visualize → Create visualization → Metric
- Metric: Average `data.params.TDS.value`
- 保存: "TDS 值"

**设备状态 State Chart:**
- Visualize → Create visualization → State chart
- X轴: Date histogram `@timestamp`
- Color by: Terms `status`
- 保存: "设备状态"

## 步骤 3：创建 Dashboard

1. 进入 Dashboard → Create dashboard
2. 点击 "Add from library"
3. 选择上面创建的可视化图表
4. 拖拽调整布局
5. 保存

## Dashboard 配置建议

### 设备状态总览 (4x4 布局)
- [环境温度] [环境湿度] [TDS 值] [设备状态]
- [温度趋势] (横跨 2 列)
- [湿度趋势] (横跨 2 列)

### 水箱监控 (4x4 布局)
- [冷水池温度趋势] [冷水池水位趋势] (各 2 列)
- [冷水池温度] [热水池温度] [净水池温度]

### 温度监控 (4x4 布局)
- [炉面温度趋势]
- [入水温度 1-4] (4 个图表)
- [出水温度 1-4] (4 个图表)

### 水泵监控 (4x4 布局)
- [水泵电流趋势] [水泵功率趋势]
- [水泵1 电流] [水泵1 功率] [水泵1 PWM]
- 其他水泵同理

### 发热管监控 (4x4 布局)
- [发热管功率趋势] [发热管电压/电流趋势]
- [发热管1 功率] [发热管1 电流] [发热管1 输出功率]
- 其他发热管同理

### 流量监控 (4x4 布局)
- [流量趋势] [流量分布]
- [流量计1] [流量计2] [流量计3]
- 其他流量计同理

### 其他设备 (4x4 布局)
- [电磁阀状态]
- [模具动作状态]
- [TDS 值] [灯状态] [状态分布]

## 字段路径说明

所有数据字段路径格式：
```
data.params.{identifier}.value
```

示例：
- 环境温度: `data.params.temp.value`
- 水池温度: `data.params.COLD_TANK_TEMP_NTC_C.value`
- 水泵电流: `data.params.PUMP_1_A.value`
- 发热管功率: `data.params.HEATER_1_POWER_W.value`

## 注意事项

1. 如果字段显示为 unmapped，需要先在 Data View 中刷新字段列表
2. 没有数据时图表为空是正常的
3. 调整时间范围查看历史数据
4. 可以复制已创建的可视化图表，修改字段快速创建相似图表
