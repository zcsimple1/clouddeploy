#!/usr/bin/env python3
"""纯 Python 实现 NTC 温度预测模型训练（无 numpy 依赖）"""
import json
import math
import random
import pickle
import os
import gzip

DATA_FILE = "/tmp/ntc_data.jsonl.gz"
MODEL_FILE = "/tmp/ntc_model.pkl"
RESULT_FILE = "/tmp/ntc_result.md"
BETTER_MODEL_FILE = "/tmp/ntc_better_model.py"

def mean(vals):
    return sum(vals) / len(vals)

def poly_features(xvals, degree):
    """生成多项式特征矩阵 [[x, x^2, ...] for each x]"""
    n = len(xvals)
    X = [[0.0] * degree for _ in range(n)]
    for i, x in enumerate(xvals):
        p = x
        for d in range(degree):
            X[i][d] = p
            p *= x
    return X

def transpose(M):
    rows, cols = len(M), len(M[0])
    return [[M[r][c] for r in range(rows)] for c in range(cols)]

def matmul(A, B):
    """A (m×n) * B (n×p) = C (m×p)"""
    m, n = len(A), len(A[0])
    p = len(B[0])
    C = [[0.0] * p for _ in range(m)]
    for i in range(m):
        for k in range(n):
            aik = A[i][k]
            if aik != 0:
                for j in range(p):
                    C[i][j] += aik * B[k][j]
    return C

def solve_normal(X, y):
    """最小二乘解 (X^T X)^(-1) X^T y 使用 Cholesky 分解"""
    n = len(X)
    d = len(X[0])  # degree

    Xt = transpose(X)  # d × n

    # XtX = X^T X  (d × d)
    XtX = [[0.0] * d for _ in range(d)]
    for i in range(d):
        for j in range(d):
            s = 0.0
            for k in range(n):
                s += Xt[i][k] * X[k][j]
            XtX[i][j] = s

    # Xty = X^T y  (d × 1)
    Xty = [0.0] * d
    for i in range(d):
        s = 0.0
        for k in range(n):
            s += Xt[i][k] * y[k]
        Xty[i] = s

    # Cholesky 分解 XtX = L * L^T
    L = [[0.0] * d for _ in range(d)]
    for i in range(d):
        for j in range(i + 1):
            s = XtX[i][j]
            for k in range(j):
                s -= L[i][k] * L[j][k]
            if i == j:
                L[i][j] = math.sqrt(max(s, 1e-10))
            else:
                L[i][j] = s / L[j][j]

    # 前向替换 L * z = Xty
    z = [0.0] * d
    for i in range(d):
        s = Xty[i]
        for j in range(i):
            s -= L[i][j] * z[j]
        z[i] = s / L[i][i]

    # 后向替换 L^T * coeffs = z
    coeffs = [0.0] * d
    for i in range(d - 1, -1, -1):
        s = z[i]
        for j in range(i + 1, d):
            s -= L[j][i] * coeffs[j]
        coeffs[i] = s / L[i][i]

    return coeffs

def predict(xvals, coeffs):
    degree = len(coeffs)
    preds = []
    for x in xvals:
        p = 0.0
        xn = x
        for d in range(degree):
            p += coeffs[d] * xn
            xn *= x
        preds.append(p)
    return preds

def main():
    print("加载数据...")
    n4_list, ot4_list = [], []
    opener = gzip.open if DATA_FILE.endswith('.gz') else open
    with opener(DATA_FILE, 'rt') as f:
        for line in f:
            row = json.loads(line)
            n4 = row.get("N4_T")
            ot4 = row.get("OT4_C")
            if n4 is not None and ot4 is not None:
                n4, ot4 = float(n4), float(ot4)
                if n4 > 0 and ot4 > 0 and ot4 < 200:
                    n4_list.append(n4)
                    ot4_list.append(ot4)

    N = len(n4_list)
    print(f"有效数据: {N} 条")

    # 采样加速（数据量过大时）
    MAX_SAMPLES = 80000
    if N > MAX_SAMPLES:
        random.seed(42)
        sample_idx = sorted(random.sample(range(N), MAX_SAMPLES))
        n4_list = [n4_list[i] for i in sample_idx]
        ot4_list = [ot4_list[i] for i in sample_idx]
        N = MAX_SAMPLES
        print(f"采样至 {N} 条（加速训练）")

    print(f"N4_T 范围: [{min(n4_list):.1f}, {max(n4_list):.1f}] °C")
    print(f"OT4_C 范围: [{min(ot4_list):.1f}, {max(ot4_list):.1f}] °C")

    # 随机打乱
    random.seed(42)
    indices = list(range(N))
    random.shuffle(indices)
    split = int(N * 0.8)

    x_all, y_all = n4_list, ot4_list

    # 训练/测试拆分
    x_train = [x_all[i] for i in indices[:split]]
    y_train = [y_all[i] for i in indices[:split]]
    x_test = [x_all[i] for i in indices[split:]]
    y_test = [y_all[i] for i in indices[split:]]

    print(f"训练集: {len(x_train)} 条, 测试集: {len(x_test)} 条")

    results = []
    best_rmse = float('inf')
    best_coeffs = None
    best_deg = 0

    for deg in [1, 2, 3]:
        X_train = poly_features(x_train, deg)
        coeffs = solve_normal(X_train, y_train)

        y_pred = predict(x_test, coeffs)
        residuals = [y_test[i] - y_pred[i] for i in range(len(y_test))]
        mae = sum(abs(r) for r in residuals) / len(residuals)
        rmse = math.sqrt(sum(r*r for r in residuals) / len(residuals))

        y_mean = mean(y_test)
        ss_res = sum(r*r for r in residuals)
        ss_tot = sum((yt - y_mean) ** 2 for yt in y_test)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        print(f"\n{'='*50}")
        print(f"  {deg}阶多项式回归")
        print(f"  系数: {[round(c, 8) for c in coeffs]}")
        print(f"  MAE:  {mae:.3f} °C")
        print(f"  RMSE: {rmse:.3f} °C")
        print(f"  R²:   {r2:.6f}")

        results.append((deg, coeffs, mae, rmse, r2))
        if rmse < best_rmse:
            best_rmse = rmse
            best_coeffs = coeffs
            best_deg = deg

    print(f"\n✅ 最佳模型: {best_deg}阶多项式 (RMSE={best_rmse:.3f}°C)")

    # 找到最佳模型的指标
    best_mae = [r[2] for r in results if r[0]==best_deg][0]
    best_r2 = [r[4] for r in results if r[0]==best_deg][0]

    # 生成预测函数
    terms = []
    for i, c in enumerate(best_coeffs):
        if i == 0:
            terms.append(f"{c:.8f} * n4_t")
        else:
            terms.append(f"{c:.8f} * n4_t**{i+1}")
    expr = " + ".join(terms)

    code = f'''# NTC -> 热电偶 温度预测模型
# 训练数据: {N} 条 (2026年6月饮水机实验)
# 精度: MAE={best_mae:.2f}°C, RMSE={best_rmse:.2f}°C, R²={best_r2:.5f}

def predict_ot4(n4_t: float) -> float:
    """用 N4_T (NTC温度) 预测 OT4_C (热电偶温度)
    Args: n4_t: NTC 温度 (°C)
    Returns: 预测热电偶温度 (°C)
    """
    return {expr}


COEFFS = {best_coeffs}

def predict_ot4_fast(n4_t: float) -> float:
    """快速预测版本"""
    result = 0.0
    xn = n4_t
    for c in COEFFS:
        result += c * xn
        xn *= n4_t
    return result
'''

    with open(RESULT_FILE, "w") as f:
        f.write(code)

    # 保存模型
    with open(MODEL_FILE, "wb") as f:
        pickle.dump({
            "degree": best_deg,
            "coeffs": best_coeffs,
            "mae": best_mae,
            "rmse": best_rmse,
            "r2": best_r2,
            "n_samples": N,
        }, f)

    print(f"\n📁 模型已保存: {MODEL_FILE}")
    print(f"📁 预测函数: {RESULT_FILE}")

    # 保存可直接使用的 Python 模块
    with open(BETTER_MODEL_FILE, "w") as f:
        f.write(code)
    print(f"📁 可导入模块: {BETTER_MODEL_FILE}")

    # 对比表
    print(f"\n{'模型':<12} {'MAE':<8} {'RMSE':<8} {'R²':<10}")
    print("-" * 38)
    names = {1: "线性", 2: "2阶多项式", 3: "3阶多项式"}
    for deg, coeffs, mae, rmse, r2 in results:
        print(f"{names[deg]:<12} {mae:<8.3f} {rmse:<8.3f} {r2:<10.6f}")

    # 举几个预测例子
    print(f"\n预测示例:")
    for n4_val in [25, 50, 80, 100]:
        pred = predict([n4_val], best_coeffs)[0]
        print(f"  N4_T={n4_val}°C → OT4_C≈{pred:.1f}°C")

if __name__ == "__main__":
    main()
