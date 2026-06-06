# NTC (N4_T) → 热电偶 (OT4_C) 温度预测模型
# 训练数据: 40,000 条 (2026年6月饮水机实验)
# 测试数据: 10,000 条
#
# 模型选择建议:
#   predict_ot4_simple(): 仅需 N4_T，精度 0.866°C，适合 Kibana Scripted Field
#   predict_ot4():        N4_T+AT+temp+N4_R，精度 0.844°C，提升有限(+2.5%)


def predict_ot4_simple(n4_t: float) -> float:
    """仅用 N4_T 预测 OT4_C (3阶多项式)
    MAE=0.866°C, RMSE=1.352°C, R²=0.973

    适用场景: Kibana Scripted Field、快速估算
    """
    return (20.418860
            - 0.258503 * n4_t
            + 0.02558798 * n4_t**2
            - 0.0001671409 * n4_t**3)


def predict_ot4(n4_t: float, at: float = 30.0, temp: float = 29.0,
                n4_r: float = 30.0) -> float:
    """N4_T + AT + temp + N4_R 混合模型
    MAE=0.844°C, RMSE=1.254°C, R²=0.977
    提升: 比纯 N4_T 多项式降低 2.5% 误差
    """
    return (21.116037
            + 0.195231 * n4_t
            + 0.01590233 * n4_t**2
            - 0.0001026491 * n4_t**3
            + 0.374042 * at        # 环境温度修正
            - 0.644548 * temp       # 模块温度修正
            - 0.009541 * n4_r)      # NTC 电阻修正


# ========== 快速测试 ==========
if __name__ == "__main__":
    # 测试几个典型温度点
    tests = [25, 40, 55, 70, 85, 100]
    print(f"{'N4_T':>6s}  {'OT4_C(简单)':>12s}  {'OT4_C(混合)':>12s}")
    print("-" * 38)
    for t in tests:
        s = predict_ot4_simple(t)
        m = predict_ot4(t)
        print(f"{t:>6.0f}  {s:>12.1f}  {m:>12.1f}")
