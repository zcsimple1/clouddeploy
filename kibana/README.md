# OneNet Kibana Dashboard 导入脚本

## 概述

此脚本用于将预配置的 OneNet 物联网设备监控 Dashboard 导入到 Kibana 中。

## Dashboard 列表

| Dashboard ID | 名称 | 说明 |
|-------------|------|------|
| dashboard-onenet-overview | 设备状态总览 | 环境温度、湿度、TDS、设备状态 |
| dashboard-onenet-tanks | 水箱监控 | 冷/热/净/接/混水池温度和水位 |
| dashboard-onenet-temperature | 温度监控 | 炉面温度、入水/出水温度、目标温度 |
| dashboard-onenet-pumps | 水泵监控 | 水泵 1-9 电流、电压、功率、PWM |
| dashboard-onenet-heaters | 发热管监控 | 发热管 1-4 电流、电压、功率 |
| dashboard-onenet-flowmeters | 流量监控 | 流量计 1-9 各路流量 |
| dashboard-onenet-others | 其他设备 | 电磁阀、模具动作、灯状态 |

## 使用方法

### 1. 上传脚本到服务器

```bash
# 在服务器上执行
cd /path/to/clouddeploy
chmod +x kibana/import_dashboards.sh
```

### 2. 运行导入脚本

```bash
# 使用默认 URL (http://101.35.135.63:5601)
./kibana/import_dashboards.sh

# 或者指定自定义 URL
KIBANA_URL=http://your-kibana-url:5601 ./kibana/import_dashboards.sh
```

### 3. 验证导入

访问 Kibana Dashboard 页面：
```
http://101.35.135.63:5601/app/dashboards/list
```

## 前置条件

1. Kibana 正在运行并可以访问
2. Elasticsearch 中已经有 OneNet 数据
3. Logstash 正在接收和处理数据

## 字段映射

根据 OneNet 物模型定义，数据字段路径为：

```
data.params.{identifier}.value
```

例如：
- 环境温度：`data.params.temp.value`
- 水池温度：`data.params.COLD_TANK_TEMP_NTC_C.value`
- 水泵电流：`data.params.PUMP_1_A.value`

## 注意事项

1. 确保 Elasticsearch 索引中已经有对应的数据字段
2. 如果字段显示为 unmapped，需要在 Kibana Data View 中刷新字段列表
3. Dashboard 需要数据才会正常显示，没有数据时可能为空

## 故障排查

### 问题：Dashboard 导入失败

**解决方案：**
- 检查 Kibana 连接：`curl http://101.35.135.63:5601/api/status`
- 检查文件权限：`ls -la kibana/dashboards/`
- 查看脚本输出错误信息

### 问题：字段显示为 unmapped

**解决方案：**
- 刷新 Kibana Data View：Stack Management → Data Views → 选择 data view → 刷新
- 检查 Elasticsearch mapping：`curl http://101.35.135.63:9200/logs-onenet-*/_mapping`
- 等待新数据写入

### 问题：图表没有数据

**解决方案：**
- 检查查询条件是否正确
- 调整时间范围
- 确认数据字段路径：`data.params.{identifier}.value`

## 自定义 Dashboard

如需修改或添加新的 Dashboard：

1. 在 Kibana 中手动创建或修改 Dashboard
2. 导出 Dashboard：Stack Management → Saved Objects → 选择 Dashboard → Export
3. 将导出的 `.ndjson` 文件放到 `kibana/dashboards/` 目录
4. 在导入脚本中添加对应的导入命令

## 文件结构

```
kibana/
├── dashboards/
│   ├── dashboard_overview.ndjson        # 设备状态总览
│   ├── dashboard_tanks.ndjson           # 水箱监控
│   ├── dashboard_temperature.ndjson     # 温度监控
│   ├── dashboard_pumps.ndjson          # 水泵监控
│   ├── dashboard_heaters.ndjson        # 发热管监控
│   ├── dashboard_flowmeters.ndjson      # 流量监控
│   ├── dashboard_others.ndjson          # 其他设备
│   └── template_dashboard_overview.json # 模板示例
├── import_dashboards.sh                 # 导入脚本
└── README.md                            # 本文档
```

## 更新日志

- 2026-02-06: 初始版本，创建 7 个监控 Dashboard
