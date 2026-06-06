# NTC → 热电偶 温度预测模型

## 数据来源

- **数据源**: ELK `logs-onenet-*` 索引（2026年6月饮水机实验）
- **样本量**: 259,486 条（训练采样 80,000 条）
- **输入字段**: `data.params.N4_T.value`（NTC 温度传感器）
- **目标字段**: `data.params.OT4_C.value`（热电偶 K 型传感器）

## 模型性能

| 模型 | MAE (°C) | RMSE (°C) | R² |
|------|----------|-----------|-----|
| 线性回归 | 1.027 | 2.037 | 0.9776 |
| 2阶多项式 | 0.927 | 1.948 | 0.9795 |
| **3阶多项式** ⭐ | **0.888** | **1.915** | **0.9802** |

## 使用方法

### 1. 直接使用预测函数

```python
from ntc_predict_model import predict_ot4, predict_ot4_fast

# NTC 读数 55°C → 预测热电偶温度
real_temp = predict_ot4(55.0)
print(f"预测: {real_temp:.1f}°C")  # → 约 55.6°C
```

### 2. 加载模型文件

```python
import pickle

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# model = {"degree": 3, "coeffs": [...], "mae": 0.888, ...}
```

### 3. 重新训练

```bash
# 拉取最新数据
python3 fetch_data.py

# 训练
python3 train_model.py
```

## 文件说明

```
ntc_predict/
├── README.md              # 本文件
├── ntc_predict_model.py   # 预测函数（可直接 import 使用）
├── model.pkl              # 训练好的模型（pickle 格式）
├── raw_data.jsonl         # 原始训练数据（本地缓存）
├── fetch_data.py          # 从 ES 拉取数据（本地运行）
├── fetch_on_server.py     # 从 ES 拉取数据（服务器端运行）
├── train_model.py         # sklearn 版训练脚本（需 numpy/sklearn）
└── train_on_server.py     # 纯 Python 版训练脚本（无依赖）
```
