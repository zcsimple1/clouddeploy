# NTC → 热电偶 温度预测模型

## 核心结论

**N4_T (NTC) 单独就能很好地预测 OT4_C (热电偶)，其他参数提升有限。**

| 模型 | 参数 | MAE | RMSE | R² |
|------|------|-----|------|-----|
| 3阶多项式 ⭐ | N4_T | 0.866°C | 1.352°C | 0.973 |
| 混合模型 | N4_T+AT+temp+N4_R | 0.844°C | 1.254°C | 0.977 |
| 8参数线性 | 全部字段 | 0.508°C | 0.966°C | 0.986 ⚠️过拟合 |

> **推荐**：Kibana Scripted Field 用纯 N4_T 多项式即可，简单且精度足够。

---

## 为什么不需要很多参数？

NTC (N4_T) 和热电偶 (OT4_C) 测量的是**同一个物理量**（水温），它们之间的差异主要来自：

1. **NTC 非线性** → 3阶多项式校准 (已解决，R²=0.97)
2. **环境温度影响** → AT/temp 仅贡献 +2.5% 改进
3. **其他参数** (湿度、电压、液位等) → 相关性极低，实际帮助微小

相关性分析：
```
N4_T  r=0.986  ← 绝对主导
N4_R  r=0.315  ← NTC 电阻，与温度非线性相关
AT    r=0.290  ← 环境温度，弱相关
temp  r=0.125  ← 模块温度，很弱
humi  r=0.080  ← 湿度，几乎无关
```

---

## Kibana Scripted Field 设置

### 打开 Kibana → Management → Index Patterns → 选择 `logs-onenet-*`

### 方案 1：简单版（推荐）

点 **Scripted Fields** → **Add scripted field**：

| 设置项 | 值 |
|--------|-----|
| Name | `N4_T0` |
| Language | `painless` |
| Type | `Number` |
| Format | `0.0` |
| Script | 见下方 |

```painless
def n4 = doc['data.params.N4_T.value'].value;
return 20.418860 - 0.258503 * n4 + 0.02558798 * n4 * n4 - 0.0001671409 * n4 * n4 * n4;
```

### 方案 2：精度版

```painless
def n4 = doc['data.params.N4_T.value'].value;
def at = doc['data.params.AT.value'].value;
def tp = doc['data.params.temp.value'].value;
def nr = doc['data.params.N4_R.value'].value;
return 21.116037 + 0.195231 * n4 + 0.01590233 * n4 * n4 - 0.0001026491 * n4 * n4 * n4 + 0.374042 * at - 0.644548 * tp - 0.009541 * nr;
```

### 对比查看

在 Discover 中选择 `N4_T0` 和 `data.params.OT4_C.value` 两列，越接近说明模型效果越好。

---

## 文件说明

```
ntc_predict/
├── ntc_predict_model.py   ← 预测函数（可直接 import）
├── train_on_server.py     ← 纯 Python 训练（无依赖）
├── fetch_on_server.py     ← 从 ELK 拉取数据
├── multivar_analysis.py   ← 多变量对比分析
└── README.md              ← 本文档
```
