#!/usr/bin/env python3
"""
NTC(N4_T) → 热电偶(OT4_C) 温度预测模型

算法思路：
1. 数据加载与清洗
2. 多项式回归拟合 N4_T → OT4_C
3. 评估模型精度
4. 输出预测函数

NTC 热敏电阻特性：
- NTC 电阻与温度呈非线性关系，通常用 Steinhart-Hart 方程
- 但 N4_T 已经是转换后的温度值，所以 N4_T 和实际温度(OT4_C)之间
  应该是接近线性但有一定的系统偏差（校准问题）
- 多项式拟合可以很好地捕捉这种关系
"""
import json
import os
import numpy as np
import pickle
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DATA_FILE = os.path.join(os.path.dirname(__file__), "raw_data.jsonl")
MODEL_FILE = os.path.join(os.path.dirname(__file__), "model.pkl")
PLOT_FILE = os.path.join(os.path.dirname(__file__), "fit_plot.png")


def load_data():
    """加载并清洗数据"""
    n4_list = []
    ot4_list = []

    with open(DATA_FILE, "r") as f:
        for line in f:
            row = json.loads(line)
            n4 = row.get("N4_T")
            ot4 = row.get("OT4_C")
            if n4 is not None and ot4 is not None:
                n4 = float(n4)
                ot4 = float(ot4)
                # 过滤明显异常值（NTC 读数为 0 或极端值）
                if n4 > 0 and ot4 > 0 and ot4 < 200:
                    n4_list.append(n4)
                    ot4_list.append(ot4)

    X = np.array(n4_list).reshape(-1, 1)
    y = np.array(ot4_list)

    print(f"加载 {len(X)} 条有效数据")
    print(f"N4_T 范围: [{X.min():.1f}, {X.max():.1f}]")
    print(f"OT4_C 范围: [{y.min():.1f}, {y.max():.1f}]")

    return X, y


def evaluate_model(model, X, y, label="", poly=None):
    """评估模型"""
    if poly:
        X_t = poly.transform(X)
    else:
        X_t = X

    y_pred = model.predict(X_t)

    mae = mean_absolute_error(y, y_pred)
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"  MAE:  {mae:.3f}°C   (平均绝对误差)")
    print(f"  RMSE: {rmse:.3f}°C   (均方根误差)")
    print(f"  R²:   {r2:.6f}   (拟合优度)")
    print(f"{'='*50}")

    return y_pred, mae, rmse, r2


def train_and_save():
    """训练并保存模型"""
    X, y = load_data()

    if len(X) < 10:
        print("数据量不足！")
        return

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # ============ 方案1: 线性回归 ============
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    _, mae1, rmse1, r2_1 = evaluate_model(lr, X_test, y_test, "线性回归")

    # ============ 方案2: 2阶多项式回归 (推荐) ============
    poly2 = PolynomialFeatures(degree=2, include_bias=False)
    X_train_poly2 = poly2.fit_transform(X_train)
    ridge2 = Ridge(alpha=0.1)
    ridge2.fit(X_train_poly2, y_train)
    y_pred2, mae2, rmse2, r2_2 = evaluate_model(ridge2, X_test, y_test, "2阶多项式回归", poly=poly2)

    # ============ 方案3: 3阶多项式回归 ============
    poly3 = PolynomialFeatures(degree=3, include_bias=False)
    X_train_poly3 = poly3.fit_transform(X_train)
    ridge3 = Ridge(alpha=0.1)
    ridge3.fit(X_train_poly3, y_train)
    y_pred3, mae3, rmse3, r2_3 = evaluate_model(ridge3, X_test, y_test, "3阶多项式回归", poly=poly3)

    # ============ 选择最佳模型 ============
    results = [
        (mae2, rmse2, r2_2, 2, ridge2, poly2, y_pred2, "2阶多项式"),
        (mae3, rmse3, r2_3, 3, ridge3, poly3, y_pred3, "3阶多项式"),
        (mae1, rmse1, r2_1, 1, lr, None, None, "线性"),
    ]
    results.sort(key=lambda x: x[1])  # 按 RMSE 排序

    best_mae, best_rmse, best_r2, best_deg, best_model, best_poly, _, best_name = results[0]

    print(f"\n✅ 最佳模型: {best_name} (RMSE={best_rmse:.3f}°C)")

    # 保存最佳模型
    model_data = {
        "model": best_model,
        "poly": best_poly,
        "degree": best_deg,
        "mae": best_mae,
        "rmse": best_rmse,
        "r2": best_r2,
    }
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model_data, f)
    print(f"模型已保存到 {MODEL_FILE}")

    # ============ 可视化 ============
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 左图：散点图 + 拟合曲线
    ax = axes[0]
    ax.scatter(X_test, y_test, s=0.5, alpha=0.3, label="真实数据")
    x_range = np.linspace(X.min(), X.max(), 500).reshape(-1, 1)
    if best_poly:
        y_curve = best_model.predict(best_poly.transform(x_range))
    else:
        y_curve = best_model.predict(x_range)
    ax.plot(x_range, y_curve, color="red", linewidth=2, label=f"{best_name}拟合")
    ax.set_xlabel("N4_T (NTC 温度 / °C)")
    ax.set_ylabel("OT4_C (热电偶温度 / °C)")
    ax.set_title(f"N4_T → OT4_C 预测模型\n{best_name}, MAE={best_mae:.2f}°C, R²={best_r2:.5f}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 右图：残差分布
    ax = axes[1]
    y_pred_best = best_model.predict(best_poly.transform(X_test) if best_poly else X_test)
    residuals = y_test - y_pred_best
    ax.scatter(y_pred_best, residuals, s=0.5, alpha=0.3)
    ax.axhline(y=0, color='red', linestyle='--')
    ax.set_xlabel("预测值 (°C)")
    ax.set_ylabel("残差 (°C)")
    ax.set_title(f"残差分布 (RMSE={best_rmse:.2f}°C)")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(PLOT_FILE, dpi=150)
    print(f"图表已保存到 {PLOT_FILE}")

    # ============ 输出预测函数代码 ============
    print("\n" + "="*50)
    print("  可直接使用的 Python 预测函数:")

    if best_deg == 1:
        coef = best_model.coef_[0]
        intercept = best_model.intercept_
        print(f"""
def predict_ot4(n4_t):
    \"\"\"用 N4_T (NTC温度) 预测 OT4_C (热电偶温度)\"\"\"
    return {coef:.6f} * n4_t + {intercept:.4f}
        """.strip())
    elif best_deg == 2:
        coef = best_model.coef_
        intercept = best_model.intercept_
        print(f"""
def predict_ot4(n4_t):
    \"\"\"用 N4_T (NTC温度) 预测 OT4_C (热电偶温度)\"\"\"
    return {coef[0]:.6f} * n4_t + {coef[1]:.8f} * n4_t**2 + {intercept:.4f}
        """.strip())
    else:
        coef = best_model.coef_
        intercept = best_model.intercept_
        terms = []
        for i, c in enumerate(coef):
            deg = i + 1
            if abs(c) > 1e-10:
                terms.append(f"{c:.8f} * n4_t**{deg}")
        expr = " + ".join(terms) + f" + {intercept:.4f}"
        print(f"""
def predict_ot4(n4_t):
    \"\"\"用 N4_T (NTC温度) 预测 OT4_C (热电偶温度)\"\"\"
    return {expr}
        """.strip())

    print("="*50)


if __name__ == "__main__":
    train_and_save()
