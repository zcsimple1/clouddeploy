# NTC -> 热电偶 温度预测模型
# 训练数据: 80000 条 (2026年6月饮水机实验)
# 精度: MAE=0.89°C, RMSE=1.92°C, R²=0.98019

def predict_ot4(n4_t: float) -> float:
    """用 N4_T (NTC温度) 预测 OT4_C (热电偶温度)
    Args: n4_t: NTC 温度 (°C)
    Returns: 预测热电偶温度 (°C)
    """
    return 1.15680558 * n4_t + -0.00480514 * n4_t**2 + 0.00003855 * n4_t**3


COEFFS = [1.1568055839899236, -0.00480514010892057, 3.8552519669704966e-05]

def predict_ot4_fast(n4_t: float) -> float:
    """快速预测版本"""
    result = 0.0
    xn = n4_t
    for c in COEFFS:
        result += c * xn
        xn *= n4_t
    return result
